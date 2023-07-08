import time
from datetime import datetime
from mdh_api import MetaDataHubManager
import sys
from import_control import ImportControl
import os
import configparser

# Get the path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the sys.path list
sys.path.append(parent_dir)
from backend.opensearch_api import OpenSearchManager

config = configparser.ConfigParser()
config.read('config.ini')


def create_managers(localhost: bool = False):
    """ This function creates the managers to handle the APIs to the MetaDataHub and the OpenSearch Node

    :param localhost: Boolean value that defines if the connection is local or on a Docker container (for testing).
    :return: Tuple containing MetaDataHubManager and OpenSearchManager objects.
    """

    mdh_manager = MetaDataHubManager(localhost=localhost)  # Create MetaDataHubManager instance
    os_manager = OpenSearchManager(localhost=localhost)
    # os_manager = OpenSearchManager(localhost=localhost, http_auth='https://metadatahub.de/projects/amos/core:UiQjMEvwok3IBuNSfgIN')  # Create OpenSearchManager instance
    return mdh_manager, os_manager


def extract_data_from_mdh(mdh_manager: MetaDataHubManager, latest_timestamp: str = False, limit: int = False) -> tuple[
    dict, list[dict], int]:
    """
    Extract data from the MetaDataHub.

    :param mdh_manager: Manager to handle the MetaDataHub API.
    :param latest_timestamp: Timestamp of the last executed import.
    :param limit: Limit of files that will be downloaded from the MetaDataHub (default = False --> no limit)
    :return: A tuple containing a dictionary of metadata-tags and their corresponding datatypes,
             a list of dictionaries containing all the metadata tags and their values for each file,
             and the amount of files downloaded.
    """
    # Download data from the MetaDataHub
    mdh_manager.download_data(timestamp=latest_timestamp, limit=limit)

    # Get the metadata datatypes, metadata data, and the number of downloaded files
    mdh_datatypes = mdh_manager.get_datatypes()
    mdh_data = mdh_manager.get_data()
    files_amount = len(mdh_data)

    return mdh_datatypes, mdh_data, files_amount


def modify_datatypes(mdh_datatypes: dict) -> dict:
    """
    Modify the mdh_datatypes dictionary for storage in OpenSearch.

    :param mdh_datatypes: A dictionary containing the corresponding datatypes to the metadata-tags from a MetaDataHub request.
    :return: A dictionary containing the corresponding OpenSearch datatypes for the metadata-tags.
    """
    modified_datatypes = {}

    # Iterate over each entry in mdh_datatypes
    for mdh_datatype in mdh_datatypes:
        name = mdh_datatype.get("name").replace(".", "_")  # Replace '.' with '_' in the metadata-tag
        mdh_type = mdh_datatype.get("type")  # Get the corresponding datatype

        # Map MetaDataHub datatype to OpenSearch datatype
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


def modify_data(mdh_data: list[dict], data_types: dict, current_time: str) -> list[(dict, id)]:
    """
    Reformat the mdh_data dictionary for storage in OpenSearch.

    :param mdh_data: A list of dictionaries containing metadata-tags for each file of a MetaDataHub request.
    :param data_types: A dictionary containing the modified OpenSearch datatypes.
    :return: A list of tuples containing the modified metadata tags and their corresponding values,
             along with the file ID.
    """
    modified_data = []  # Initialize the resulting list

    for file_data in mdh_data:  # Iterate over each file's data in mdh_data
        metadata = file_data.get("metadata", [])  # Get the metadata for the current file
        file_info = {}  # Initialize the dictionary to store the modified metadata tags

        id = None  # Initialize the file ID

        for meta in metadata:  # Iterate over each metadata tag
            # Get the name and replace '.' with '_' to avoid parsing errors
            name = str(meta.get("name")).replace(".", "_")
            value = meta.get("value")  # Get the corresponding value for the metadata tag

            if name in data_types:  # Check if the metadata tag has a corresponding data type
                if name == "SourceFile":
                    id = str(value)  # Set the ID to the value of the "SourceFile" tag

                if data_types[name] == 'date':  # Check if the data type is 'date'
                    # Parse the value as a datetime object
                    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    # Format the datetime as a string for storage in OpenSearch
                    value = date.strftime("%Y-%m-%dT%H:%M:%S")
                elif data_types[name] == 'float':  # Check if the data type is 'float'
                    value = float(value)  # Convert the value to a float

                if name and value:  # Check if both the name and value are valid
                    file_info[name] = value  # Store the modified metadata tag and its value in the file_info dictionary
        file_info['timestamp'] = current_time

        modified_data.append(
            (file_info, id))  # Append the modified metadata and the ID as a tuple to the modified_data list

    return modified_data


def upload_data(instance_name: str, os_manager: OpenSearchManager, data_types: dict, data: list[dict],
                files_amount: int) -> int:
    """
    Uploads the modified data from MetaDataHub to OpenSearch using the bulk API.

    Args:
        instance_name (str): Name of the instance (equivalent to index name in OpenSearch Node).
        os_manager (OpenSearchManager): Manager to handle the OpenSearch API.
        data_types (dict): Dictionary of metadata tags and their corresponding data types.
        data (list[dict]): List of dictionaries containing metadata tags and their values for each file.
        files_amount (int): Total number of files (equal to the length of data).

    Returns:
        int: Number of successfully imported files.
    """

    # Create an index for the new data in OpenSearch
    os_manager.create_index(index_name=instance_name)

    # Update the index mapping with the data types
    os_manager.update_index(index_name=instance_name, data_types=data_types)

    chunk_size = 10000  # Size of chunks the data will be split into
    imported_files = 1  # Counter for files that are successfully imported

    for i in range(0, files_amount, chunk_size):
        # Split the data into chunks
        chunk_data = data[i:i + chunk_size]

        # Perform a bulk request to store the new data in OpenSearch
        response = os_manager.perform_bulk(index_name=instance_name, data=chunk_data)

        # Increment the imported files count by the number of successfully imported files in the response
        imported_files += len(response.get('items', []))

    return imported_files


def print_import_pipeline_results(start_time: float):
    """
    Prints the results of the import pipeline execution.

    Args:
        start_time (float): Start time of the pipeline execution.
        import_info (dict): Information about the import status.

    """
    # if not import_info["Status"] == "Successful":
    #     print("Import not successfull after retry.")
    print("--> Pipeline execution finished!")
    print("--> Pipeline took ", "%s seconds" % (time.time() - start_time), " to execute!")


def execute_pipeline(import_control: ImportControl):
    """
        This function executes the complete import-pipeline by executing 4 steps:
        1. connecting to the OpenSearch Node and the MetaDataHub
        2. Downloading the data from the MetaDataHub
        3. Modifying the data in a format that is readable for OpenSearch
        4. Uploading the modified data into the OpenSearch Node
    """

    print("---------------------- Import-Pipeline ----------------------")
    print("Start executing the pipeline ...")

    # the instance of the MetaDataHub in which the search is performed
    # instance_name = "amoscore"
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    instance_name = "amoscore"  # config.get('General','default_index_name')

    mdh_manager, os_manager = create_managers(localhost=False)  # config.getboolean('General','localhost'))

    latest_timestamp = os_manager.get_latest_timestamp(index_name=instance_name)

    mdh_datatypes, mdh_data, files_amount = extract_data_from_mdh(mdh_manager=mdh_manager, limit=15)

    files_in_mdh = mdh_manager.get_total_files_count()
    files_in_os = os_manager.count_files(index_name=instance_name)
    import_control.create_import(files_in_os=files_in_os, files_in_mdh=files_in_mdh)

    data_types = modify_datatypes(mdh_datatypes=mdh_datatypes)  # modify the datatypes so they fit in OpenSearch
    data = modify_data(mdh_data=mdh_data, data_types=data_types,
                       current_time=current_time)  # modify the data so it fits in OpenSearch

    # Loading the data into OpenSearch
    imported_files = upload_data(instance_name=instance_name, os_manager=os_manager, data_types=data_types, data=data,
                                 files_amount=files_amount)

    import_control.update_import(imported_files=imported_files)

    # return import_info

    print("----> Pipeline finished!")
    print("---------------------- Import-Pipeline ----------------------")


def manage_import_pipeline():
    caller = os.environ.get("CALLER", "manual")

    import_control = ImportControl()

    if not caller == "cronjob":  # Docker container gets started
        # 1. Case: Initial start
        if import_control.is_first_import():
            execute_pipeline(import_control)
        else:
            if not import_control.last_import_successful():
                execute_pipeline(import_control)
    else:
        print("Pipeline called by Cronjob")
        execute_pipeline(import_control)


if __name__ == "__main__":
    manage_import_pipeline()


# TODO: Put current time into modify data

def reformat_metadata(mdh_data: list[dict], data_types: dict, current_time: str) -> list[(dict, id)]:
    """
    Reformat the mdh_data dictionary for storage in OpenSearch.

    :param mdh_data: A list of dictionaries containing metadata-tags for each file of a MetaDataHub request.
    :param data_types: A dictionary containing the modified OpenSearch datatypes.
    :param current_time: The current time in string format.
    :return: A list of tuples containing the modified metadata tags and their corresponding values,
             along with the file ID.
    """
    modified_data = []  # Initialize the resulting list

    for file_data in mdh_data:  # Iterate over each file's data in mdh_data
        metadata = file_data.get("metadata", [])  # Get the metadata for the current file
        file_info = {}  # Initialize the dictionary to store the modified metadata tags

        id = None  # Initialize the file ID

        for meta in metadata:  # Iterate over each metadata tag
            # Get the name and replace '.' with '_' to avoid parsing errors
            name = str(meta.get("name")).replace(".", "_")
            value = meta.get("value")  # Get the corresponding value for the metadata tag

            if name in data_types:  # Check if the metadata tag has a corresponding data type
                if name == "SourceFile":
                    id = str(value)  # Set the ID to the value of the "SourceFile" tag

                if data_types[name] == 'date':  # Check if the data type is 'date'
                    # Parse the value as a datetime object
                    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    # Format the datetime as a string for storage in OpenSearch
                    value = date.strftime("%Y-%m-%dT%H:%M:%S")
                elif data_types[name] == 'float':  # Check if the data type is 'float'
                    value = float(value)  # Convert the value to a float

                if name and value:  # Check if both the name and value are valid
                    file_info[name] = value  # Store the modified metadata tag and its value in the file_info dictionary
        file_info['timestamp'] = current_time

        modified_data.append(
            (file_info, id))  # Append the modified metadata and the ID as a tuple to the modified_data list

    return modified_data

# TODO: (optional) make multiple used variables global
