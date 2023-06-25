import time
from datetime import datetime
from mdh_api import MetaDataHubManager
import sys
import os

# Get the path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the sys.path list
sys.path.append(parent_dir)
from backend.opensearch_api import OpenSearchManager


def create_managers(localhost=False):
    """Create the managers to handle the APIs to the MetaDataHub and the OpenSearch Node.

    :param localhost: Boolean value that defines if the connection is done locally or on a Docker container (for testing)
    :return: Instances of the MetaDataHubManager and the OpenSearchManager
    """
    mdh_manager = MetaDataHubManager(localhost=localhost)  # Create a manager to handle the MetaDataHub API
    os_manager = OpenSearchManager(localhost=localhost)  # Create a manager to handle the OpenSearch API
    return mdh_manager, os_manager


def extract_data_from_mdh(mdh_manager: MetaDataHubManager, latest_timestamp: str) -> tuple[dict, list[dict], int]:
    """Extract the data from the MetaDataHub.

    :param mdh_manager: Manager to handle the MetaDataHub API
    :param latest_timestamp: Timestamp of the last executed import
    :return: A tuple containing the metadata-tag datatypes, a list of metadata tags and values for each file, and the
             number of files downloaded
    """
    mdh_manager.download_data(timestamp=latest_timestamp, limit=20)
    mdh_datatypes = mdh_manager.get_datatypes()
    mdh_data = mdh_manager.get_data()
    files_amount = len(mdh_data)
    return mdh_datatypes, mdh_data, files_amount


def modify_datatypes(mdh_datatypes: dict) -> dict:
    """Modify the mdh_datatypes dictionary for storage in OpenSearch.

    :param mdh_datatypes: A dictionary containing the corresponding datatypes to the metadata-tags from a MetaDataHub request
    :return: A dictionary containing the corresponding OpenSearch datatypes for the metadata-tags
    """
    modified_datatypes = {}
    for mdh_datatype in mdh_datatypes:
        name = mdh_datatype.get("name").replace(".", "_")
        mdh_type = mdh_datatype.get("type")
        if mdh_type == 'num':
            modified_datatypes[name] = 'float'
        elif mdh_type == 'ts':
            modified_datatypes[name] = 'date'
        elif mdh_type == 'str':
            modified_datatypes[name] = 'text'
        else:
            modified_datatypes[name] = 'text'
        if len(modified_datatypes) >= 900:
            break
    return modified_datatypes


def modify_data(mdh_data: list[dict], data_types: dict) -> list[(dict, id)]:
    """Modify the mdh_data dictionary for storage in OpenSearch.

    :param mdh_data: A list of dictionaries containing metadata-tags for every file of a MetaDataHub request
    :param data_types: A dictionary containing the modified OpenSearch datatypes
    :return: A list of dictionaries containing the modified metadata tags and their corresponding values
    """
    id = "default_id"
    modified_data = []
    for index, file_data in enumerate(mdh_data, start=1):
        metadata = file_data.get("metadata", [])
        file_info = {}
        for meta in metadata:
            name = str(meta.get("name")).replace(".", "_")
            value = meta.get("value")
            if name in data_types:
                if name == "SourceFile":
                    id = str(value)
                if data_types[name] == 'date':
                    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    value = str(date.strftime("%Y-%m-%d" "T" "%H:%M:%S"))
                elif data_types[name] == 'float':
                    value = float(value)
                if name and value:
                    file_info[name] = value
        modified_data.append((file_info, id))
    return modified_data


def upload_data(instance_name: str, os_manager: OpenSearchManager, data_types: dict, data: list[dict], files_amount: int) -> int:
    """Upload the modified data from the MetaDataHub into the OpenSearch Node using the bulk API.

    :param instance_name: Name of the instance (equals index name in OpenSearch Node)
    :param os_manager: Manager to handle the OpenSearch API
    :param data_types: Dictionary of metadata-tags and their corresponding datatypes
    :param data: List of dictionaries containing metadata-tags and their values for each file
    :param files_amount: Number of files (equals length of data)
    :return: Number of successfully imported files
    """
    os_manager.create_index(index_name=instance_name)
    os_manager.update_index(index_name=instance_name, data_types=data_types)
    chunk_size = 10000
    imported_files = 0
    for i in range(0, files_amount, chunk_size):
        response = os_manager.perform_bulk(index_name=instance_name, data=data[i:i + chunk_size])
        imported_files += len(response['items'])
    return imported_files


def execute_pipeline():
    """
    Execute the complete import pipeline by performing the following steps:
    1. Connect to the OpenSearch Node and the MetaDataHub API
    2. Download data from the MetaDataHub
    3. Modify the data in a format suitable for OpenSearch
    4. Upload the modified data into the OpenSearch Node
    """
    instance_name = "amoscore"
    print("1. Connecting to the OpenSearch Node and the MetaDataHub API.")
    start_time_connecting = time.time()
    mdh_manager, os_manager = create_managers(localhost=False)
    print("--> Finished connecting to the OpenSearch Node and the MetaDataHub API!")
    print("--> Time needed: %s seconds!" % (time.time() - start_time_connecting))

    latest_timestamp = '1111-11-11 11:11:11'
    print(f"2. Downloading data from '{instance_name}' in MdH that was added after "
          f"{(latest_timestamp, 'begin')[latest_timestamp == '1111-11-11 11:11:11']}.")
    start_time_extracting = time.time()
    mdh_datatypes, mdh_data, files_amount = extract_data_from_mdh(mdh_manager=mdh_manager,
                                                                  latest_timestamp=latest_timestamp)
    print(f"--> Finished downloading data from MdH!")
    print(f"--> {files_amount} files with a total of {len(mdh_datatypes)} metadata-tags have been downloaded.")
    print("--> Time needed: %s seconds!" % (time.time() - start_time_extracting))

    print("3. Modifying the data.")
    start_time_modifying = time.time()
    data_types = modify_datatypes(mdh_datatypes=mdh_datatypes)
    data = modify_data(mdh_data=mdh_data, data_types=data_types)
    print("--> Finished modifying the data!")
    print(f"--> {files_amount} files with a total of {len(data_types)} metadata-tags have been modified.")
    print("--> Time needed: %s seconds!" % (time.time() - start_time_modifying))

    print(f"4. Uploading the modified data into the OpenSearch Node with the instance name '{instance_name}'.")
    start_time_uploading = time.time()
    imported_files = upload_data(instance_name=instance_name, os_manager=os_manager, data_types=data_types,
                                 data=data, files_amount=files_amount)
    print("--> Finished uploading the modified data into the OpenSearch Node!")
    print(f"--> {imported_files} files have been successfully imported.")
    print("--> Time needed: %s seconds!" % (time.time() - start_time_uploading))


if __name__ == '__main__':
    execute_pipeline()
