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
    """ This function creates the managers to handle the APIs to the MetaDataHub and the OpenSearch Node

    :param localhost: bool value that defines if the connection is done locally or on a Docker container (for testing)
    :return: each an object for the MetaDataHub and the OpenSearch manager
    """
    mdh_manager = MetaDataHubManager(localhost=localhost)  # create a manager for handling the MetaDataHub API
    os_manager = OpenSearchManager(localhost=localhost)  # create a manager for handling the OpenSearch API
    return mdh_manager, os_manager


def extract_data_from_mdh(mdh_manager: MetaDataHubManager, latest_timestamp: str) -> tuple[dict, list[dict], int]:
    """ This function downloads the data from the MetaDataHub

    :param mdh_manager: Manager to handle the MetaDataHub Api :param latest_timestamp: timestamp of the last executed
    import
    :return: a dictionary of metadata-tags and their corresponding datatypes, a list of dictionaries
    containing all the metadata tags and their values for each file, the amount of files downloaded
    """
    mdh_manager.download_data(timestamp=latest_timestamp, limit=20)
    mdh_datatypes = mdh_manager.get_datatypes()  # get all mdh_datatypes of the request
    mdh_data = mdh_manager.get_data()  # get all mdh_data from the request
    files_amount = len(mdh_data)  # amounts of files downloaded from MdH

    return mdh_datatypes, mdh_data, files_amount


def modify_datatypes(mdh_datatypes: dict) -> dict:
    """
    Reformatting the mdh_datatypes dictionary for storage in OpenSearch.

    :param mdh_datatypes: A dictionary containing the corresponding datatypes to
    he metadata-tags from a MetaDataHub
    request. :return: A dictionary containing the corresponding OpenSearch datatypes
    for the metadata-tags.
    """
    modified_datatypes = {}  # init the resulting dictionary
    # Check if the file has been modified or added since the last import
    ##if file_timestamp > last_import_timestamp:
    for mdh_datatype in mdh_datatypes:  # loop over all entries of the mdh_datatypes dictionary
        name = mdh_datatype.get("name").replace(".", "_")  # get the metadata-tag and replace the '.' with '_'
        mdh_type = mdh_datatype.get("type")  # get the corresponding datatype
        # assign the correct OpenSearch datatype
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
    """
    Reformatting the mdh_data dictionary for storage in OpenSearch.

    :param mdh_data: A list of dictionaries that contains all metadata-tags for
    every file of a MetaDataHub request.
    :param data_types: A dictionary containing the modified OpenSearch datatypes.
    :return: A list of dictionaries containing the modified metadata tags and their corresponding values.
    """
    # Signal that there is no specific id
    id = "default_id"

    modified_data = []  # init the resulting list
    for index, file_data in enumerate(mdh_data, start=1):  # Loop over all files of mdh_data
        metadata = file_data.get("metadata", [])  # get the metadata for each file
        file_info = {}  # init the dictionary in which the metadata will be stored
        for meta in metadata:  # loop over every metadata-tag
            name = str(meta.get("name")).replace(".",
                                                 "_")  # get the name and replace '. with '_' to avoid parsing errors
            value = meta.get("value")  # get the corresponding value for the metadata-tag
            # set correct datatypes
            if name in data_types:
                if name == "SourceFile":
                    id = str(value)

                if data_types[name] == 'date':
                    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")  # get the correct datetime format
                    value = str(date.strftime(
                        "%Y-%m-%d" "T" "%H:%M:%S"))  # make the datetime a string so it can be stored in OpenSearch
                elif data_types[name] == 'float':
                    value = float(value)
                if name and value:
                    file_info[name] = value

        modified_data.append((file_info, id))

    return modified_data


def upload_data(instance_name: str, os_manager: OpenSearchManager, data_types: dict, data: list[dict], files_amount: int) -> int:
    """ This function uploads the modified data from the MetaDataHub into the OpenSearch Node using the bulk API

    :param instance_name: name of the instance (equals index name in Opensearch Node)
    :param os_manager: Manager to handle the OpenSearch API
    :param data_types: dictionary of all metadata-tags and their corresponding datatypes
    :param data: list of dictionaries containing all metadata-tags and their values for each file
    :param files_amount: amount of files (equals length of data)
    :return: integer containing the amount of all successfully imported files
    """
    os_manager.create_index(index_name=instance_name)  # create an index for the new data
    os_manager.update_index(index_name=instance_name, data_types=data_types)
    # due to performance reasons big amounts of data have to be split into smaller peaces
    chunk_size = 10000  # size of peaces the data will be split into
    imported_files = 0  # counter for files that are successfully imported
    for i in range(0, files_amount, chunk_size):  # loop over every new data-peace
        response = os_manager.perform_bulk(index_name=instance_name,
                                           data=data[
                                                i:i + chunk_size])  # perform a bulk request to store the new data in OpenSearch
        imported_files += len(response['items'])

    return imported_files


def execute_pipeline():
    """
        This function executes the complete import-pipeline by executing 4 steps:
        1. connecting to the OpenSearch Node and the MetaDataHub
        2. Downloading the data from the MetaDataHub
        3. Modifying the data in a format that is readable for OpenSearch
        4. Uploading the modified data into the OpenSearch Node
    """

    # the instance of the MetaDataHub in which the search is performed
    instance_name = "amoscore"

    # getting the manager to handle the APIs
    print("1. Start to connect to the OpenSearch Node and the MetaDataHub API.")
    start_time_connecting = time.time()
    mdh_manager, os_manager = create_managers(localhost=False)
    print("--> Finished to connect to the OpenSearch Node and the MetaDataHub API!")
    print("--> Time needed: %s seconds!" % (time.time() - start_time_connecting))

    # get the timestamp of the latest data import
    # latest_timestamp = os_manager.get_latest_timestamp(index_name=instance_name)
    latest_timestamp = '1111-11-11 11:11:11'
    # MdH data extraction
    print(f"2. Starting to download data from '{instance_name}' in MdH that was added after "
          f"{(latest_timestamp, 'begin')[latest_timestamp == '1111-11-11 11:11:11']}.")
    start_time_extracting = time.time()
    mdh_datatypes, mdh_data, files_amount = extract_data_from_mdh(mdh_manager=mdh_manager,
                                                                  latest_timestamp=latest_timestamp)
    print(f"--> Finished to download data from MdH!")
    print(f"--> {files_amount} files with a total of {len(mdh_datatypes)} metadata-tags have been downloaded.")
    print("--> Time needed: %s seconds!" % (time.time() - start_time_extracting))

    # Modifying the data into correct format
    print("3. Starting to modify the data.")
    start_time_modifying = time.time()
    data_types = modify_datatypes(mdh_datatypes=mdh_datatypes)  # modify the datatypes so they fit in OpenSearch
    data = modify_data(mdh_data=mdh_data, data_types=data_types)  # modify the data so it fits in OpenSearch
    print("--> Finished to modify the data!")
    print("--> Time needed: %s seconds!" % (time.time() - start_time_modifying))

    # Loading the data into OpenSearch
    print("4. Starting to store data in OpenSearch.")
    start_time_loading = time.time()
    imported_files = upload_data(instance_name=instance_name, os_manager=os_manager, data_types=data_types, data=data,
                                 files_amount=files_amount)
    print("--> Finished to store data in OpenSearch!")
    print(f"--> {imported_files} of {files_amount} files have been imported into the OpenSearch Node!")
    if not imported_files == files_amount:
        print(f"Not all files could be imported successfully, please repeat import!")
    print("--> Time needed: %s seconds!" % (time.time() - start_time_loading))


if __name__ == "__main__":
    print("---------------------- Import-Pipeline ----------------------")
    start_time = time.time()
    execute_pipeline()
    print("--> Pipeline execution finished!")
    print("--> Pipeline took ", "%s seconds" % (time.time() - start_time), " to execute!")
    print("---------------------- Import-Pipeline ----------------------")
