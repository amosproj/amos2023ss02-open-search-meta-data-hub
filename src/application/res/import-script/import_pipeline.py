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
from backend.configuration import get_config_values



def create_managers(localhost: bool = False):
    """ This function creates the managers to handle the APIs to the MetaDataHub and the OpenSearch Node

    :param localhost: Boolean value that defines if the connection is local or on a Docker container (for testing).
    :return: Tuple containing MetaDataHubManager and OpenSearchManager objects.
    """

    mdh_manager = MetaDataHubManager(localhost=localhost)  # Create MetaDataHubManager instance
    os_manager = OpenSearchManager(localhost=localhost)
    return mdh_manager, os_manager


def extract_metadata_tags_from_mdh(mdh_manager: MetaDataHubManager, amount_of_tags: int = 900) -> list[dict]:
    """
    Extract the most frequently used metadata tags from the MetaDataHub.

    :param mdh_manager: Manager to handle the MetaDataHub API.
    :param amount_of_tags: amount of tags that will be downloaded from the MetaDataHub (default = 900)
    :return: A list of dictionaries of the most frequently metadata-tags and their corresponding datatypes
    """

    # Download data from the MetaDataHub
    mdh_manager.download_metadata_tags(amount_of_tags=amount_of_tags)

    # Get the metadata tags, and the number of downloaded files
    mdh_tags = mdh_manager.get_metadata_tags()

    return mdh_tags


def extract_data_from_mdh(mdh_manager: MetaDataHubManager, latest_timestamp: str = False, limit: int = False,
        offset: int = False, selected_tags: list = None, file_type: str = False) -> tuple[list[dict], int]:
    """
    Extract data from the MetaDataHub.

    :param mdh_manager: Manager to handle the MetaDataHub API.
    :param latest_timestamp: Timestamp of the last executed import.
    :param limit: Limit of files that will be downloaded from the MetaDataHub (default = False --> no limit)
    :return: A tuple containing a list of dictionaries containing all the metadata tags and their values for each file,
             and the amount of files downloaded.
    """

    # Download data from the MetaDataHub
    mdh_manager.download_data(timestamp=latest_timestamp, limit=limit, selected_tags=selected_tags, file_type=file_type)

    # Get the data, and the number of downloaded files
    mdh_data = mdh_manager.get_data()
    files_amount = mdh_manager.get_return_files_count()

    return mdh_data, files_amount


def modify_metadata_tags(mdh_tags: list) -> dict:
    """
    Modify the mdh_datatypes dictionary for storage in OpenSearch.

    :param mdh_datatypes: A list dictionaries containing the corresponding datatypes to the metadata-tags from a MetaDataHub request.
    :return: A dictionary containing the corresponding OpenSearch datatypes for the metadata-tags.
    """
    modified_tags = {}

    # Iterate over each entry in mdh_datatypes
    for mdh_tag in mdh_tags:
        name = mdh_tag.get("name").replace(".", "_")  # Replace '.' with '_' in the metadata-tag
        mdh_type = mdh_tag.get("type")  # Get the corresponding datatype

        # Map MetaDataHub datatype to OpenSearch datatype
        if mdh_type == 'num':
            modified_tags[name] = 'float'
        elif mdh_type == 'ts':
            modified_tags[name] = 'date'
        elif mdh_type == 'str':
            modified_tags[name] = 'text'
        else:
            modified_tags[name] = 'text'
    return modified_tags


def modify_data(mdh_data: list[dict], metadata_tags: dict, current_time: str) -> list[(dict, id)]:
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

            if name in metadata_tags:  # Check if the metadata tag exists in OpenSearch
                if name == "SourceFile":
                    id = str(value)  # Set the ID to the value of the "SourceFile" tag

                if metadata_tags[name] == 'date':  # Check if the data type is 'date'
                    # Parse the value as a datetime object
                    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    # Format the datetime as a string for storage in OpenSearch
                    value = date.strftime("%Y-%m-%dT%H:%M:%S")
                elif metadata_tags[name] == 'float':  # Check if the data type is 'float'
                    value = float(value)  # Convert the value to a float
                else:
                    value = str(value)

                if name and value:  # Check if both the name and value are valid
                    file_info[name] = value  # Store the modified metadata tag and its value in the file_info dictionary
        file_info['timestamp'] = current_time

        modified_data.append(
            (file_info, id))  # Append the modified metadata and the ID as a tuple to the modified_data list

    return modified_data


def upload_data(index_name: str, os_manager: OpenSearchManager, metadata_tags: dict, data: list[(dict, id)],
                files_amount: int) -> tuple[any, list[dict]]:
    """
    Uploads the modified data from MetaDataHub to OpenSearch using the bulk API.

    Args:
        index_name (str): Name of the instance (equivalent to index name in OpenSearch Node).
        os_manager (OpenSearchManager): Manager to handle the OpenSearch API.
        metadata_tags (dict): Dictionary of metadata tags and their corresponding data types.
        data (list[dict]): List of dictionaries containing metadata tags and their values for each file.
        files_amount (int): Total number of files (equal to the length of data).

    Returns:
        int: Number of successfully imported files.
    """

    # Create an index for the new data in OpenSearch
    os_manager.create_index(index_name=index_name)

    # Update the index mapping with the data types
    os_manager.update_index(index_name=index_name, data_types=metadata_tags)

    chunk_size = 1000  # Size of chunks the data will be split into

    failed_imports = []
    for i in range(0, files_amount, chunk_size):
        # Split the data into chunks
        chunk_data = data[i:i + chunk_size]

        # Perform a bulk request to store the new data in OpenSearch
        response = os_manager.perform_bulk(index_name=index_name, data=chunk_data)

        if response is not None and response['errors']:
            failed_imports.append((response, chunk_data))

    return failed_imports


def print_import_pipeline_results(start_time: float, imported_files: int):
    """
    Prints the results of the import pipeline execution.

    Args:
        start_time (float): Start time of the pipeline execution.
        imported_files (int): Amount of successful imported files.

    """
    # if not import_info["Status"] == "Successful":
    #     print("Import not successfull after retry.")
    print("--> Pipeline execution finished!")
    print("--> Pipeline took ", "%s seconds" % (time.time() - start_time), " to execute!")
    print(f"--> Pipeline imported {imported_files} files!")
    print("---------------------- Import-Pipeline ----------------------")


def handle_failed_imports(os_manager: OpenSearchManager, index_name: str, failed_imports: list[any]):
    """
    Handle the failed imports of the import pipeline execution, by retrying the import

    Args:
        os_manager (OpenSearchManager): Manager to handle the OpenSearch API.
        index_name (str): Name of the instance (equivalent to index name in OpenSearch Node).
        failed_imports (list): List of all bulk requests that contained at least one failed import

    """
    for response, chunk_data in failed_imports:
        for item in response["items"]:
            if "error" in item["create"]:
                error = item["create"]["error"]["type"]
                error_id = item["create"]["_id"]
                # skip errors caused by a version conflict (file already exists)
                if not error == "version_conflict_engine_exception":
                    retry_data = []
                    for file, id in chunk_data:
                        if error_id == id:
                            retry_data.append((file, id))
                    response = os_manager.perform_bulk(index_name=index_name, data=retry_data)


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
    start_time = time.time()

    # get config values
    options = get_config_values()
    index_name = options['index_name']
    limit = options['limit']
    localhost = options['localhost']
    only_new_data = options['only_new_data']
    only_selected_tags = options['only_selected_tags']
    if only_selected_tags:
        selected_tags = options['selected_tags']
    else:
        selected_tags = []

    file_types = options['file_types']

    # get current time
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # create manager
    mdh_manager, os_manager = create_managers(localhost=localhost)

    # get the current amount of files in os
    files_in_os = os_manager.count_files(index_name=index_name)

    # get the date of the last import if only new data should be imported
    if only_new_data:
        latest_timestamp = os_manager.get_latest_timestamp(index_name=index_name)
    else:
        latest_timestamp = False

    # get the current amount of fields (metadata tags) in os
    fields_in_os = os_manager.get_all_fields(index_name=index_name)

    # get the metadata tags and their datatypes either from the mdh itself (initial import) or from OpenSearch
    if not fields_in_os is None:  # this is not the first (initial) import
        metadata_tags = {}
        for field in fields_in_os:
            metadata_tags[field] = os_manager.get_datatype(index_name=index_name, field_name=field)
    else: # this is executed if it is the first import
        mdh_tags = extract_metadata_tags_from_mdh(mdh_manager=mdh_manager)
        metadata_tags = modify_metadata_tags(mdh_tags=mdh_tags)  # modify the datatypes so they fit in OpenSearch

    #file_types = ["XML","JPEG", "TXT"] #TODO
    limit = int(limit / len(file_types))

    for file_type in file_types:

        # extract the data from the mdh
        mdh_data, files_amount = extract_data_from_mdh(mdh_manager=mdh_manager, limit=limit, latest_timestamp=latest_timestamp, selected_tags=selected_tags, file_type=file_type)

        # get the amount of files that exist in the mdh core
        files_in_mdh = mdh_manager.get_total_files_count()

        # create a new import in the 'import.dictionary' file (monitoring purposes)
        import_control.create_import(files_in_os=files_in_os, files_in_mdh=files_in_mdh)

        # modify the data so it can be easily stored in OpenSearch
        data = modify_data(mdh_data=mdh_data, metadata_tags=metadata_tags,
                           current_time=current_time)

        # Loading the data into OpenSearch
        failed_imports = upload_data(index_name=index_name, os_manager=os_manager, metadata_tags=metadata_tags,
                                     data=data,
                                     files_amount=files_amount)

        # wait for two seconds to avoid synchronization problems
        time.sleep(2)

        # handle the failed imports
        handle_failed_imports(os_manager, index_name, failed_imports)

        # files in os after import
        imported_files = os_manager.count_files(index_name=index_name) - files_in_os

        # update the import in the 'import.dictionary' file
        import_control.update_import(imported_files=imported_files)

    # print the import results
    print_import_pipeline_results(start_time=start_time, imported_files=imported_files)


def manage_import_pipeline():
    import_control = ImportControl()
    execute_pipeline(import_control)


if __name__ == "__main__":
    manage_import_pipeline()
