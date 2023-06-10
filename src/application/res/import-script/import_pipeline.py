from datetime import datetime
from mdh_api import MetaDataHubManager
import sys
import os
from datetime import datetime
# Get the path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the sys.path list
sys.path.append(parent_dir)

from backend.opensearch_api import OpenSearchManager
from mdh_api import MetaDataHubManager



def modify_datatypes(mdh_datatypes: dict) -> dict:
    """
    Reformatting the mdh_datatypes dictionary for storage in OpenSearch.

    :param mdh_datatypes: A dictionary containing the corresponding datatypes to
    the metadata-tags from a MetaDataHub request.
    :return: A dictionary containing the corresponding OpenSearch datatypes for the metadata-tags.
    """
    modified_datatypes = {}
    for mdh_datatype in mdh_datatypes:
        name = mdh_datatype.get("name").replace(".", "_")
        mdh_type = mdh_datatype.get("type")
        modified_datatypes[name] = 'float' if mdh_type == 'num' else 'date' if mdh_type == 'ts' else 'text'
    return modified_datatypes


def filter_modified_data(mdh_data, data_types, last_import_timestamp):
    filtered_data = []
    for file_data in mdh_data:
        metadata = file_data.get("metadata", [])
        file_info = {}
        file_timestamp = file_data.get("timestamp")

        # Check if the file has been modified or added since the last import
        if compare_dates(file_timestamp, last_import_timestamp):
            for meta in metadata:
                name = str(meta.get("name")).replace(".", "_")
                value = meta.get("value")
                if data_types[name] == 'date':
                    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    value = str(date.utcnow().strftime("%Y-%m-%d" "T" "%H:%M:%S"))
                elif data_types[name] == 'float':
                    value = float(value)
                if name and value:
                    file_info[name] = value
            filtered_data.append(file_info)

    return filtered_data


def modify_data(mdh_data: list[dict], data_types: dict, last_import_timestamp: datetime) -> list[dict]:
    """
    Reformatting the mdh_data dictionary for storage in OpenSearch.

    :param mdh_data: A list of dictionaries that contains all metadata-tags for
    every file of a MetaDataHub request.
    :param data_types: A dictionary containing the modified OpenSearch datatypes.
    :param last_import_timestamp: The timestamp of the last import to OpenSearch.
    :return: A list of dictionaries containing the modified metadata tags and their corresponding values.
    """

    modified_data = []  # init the resulting list
    for file_data in mdh_data:
        metadata = file_data.get("metadata", [])  # get the metadata for each file
        file_info = {}  # init the dictionary in which the metadata will be stored
        file_timestamp = file_data.get("timestamp")

        # Check if the file has been modified or added since the last import
        if compare_dates(file_timestamp, last_import_timestamp):
            for meta in metadata:  # loop over every metadata-tag
                name = str(meta.get("name")).replace(".",
                                                     "_")  # get the name and replace '. with '_' to avoid parsing errors
                value = meta.get("value")  # get the corresponding value for the metadata-tag
                # set correct datatypes
                if data_types[name] == 'date':
                    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")  # get the correct datetime format
                    value = str(date.utcnow().strftime(
                        "%Y-%m-%d" "T" "%H:%M:%S"))  # make the datetime a string so it can be stored in OpenSearch
                elif data_types[name] == 'float':
                    value = float(value)
                if name and value:
                    file_info[name] = value

            modified_data.append(file_info)

    return modified_data


def get_last_import_timestamp():
    os_manager = OpenSearchManager(localhost=False)  # create a manager for handling the OpenSearch API
    index_name = os_manager.get_index_name()  # retrieve the index name where the data is stored
    last_import_timestamp = os_manager.get_last_import_timestamp(index_name)
    return last_import_timestamp


def compare_dates(opensearch_date: datetime, py_date: datetime) -> bool:
    """
    Compare an OpenSearch date with a Python datetime.

    :param opensearch_date: OpenSearch date as datetime object.
    :param py_date: Python datetime object.
    :return: True if the OpenSearch date is after the Python datetime, False otherwise.
    """
    return opensearch_date > py_date


if __name__ == "__main__":
    print("Start importing...")
    mdh_manager = MetaDataHubManager(localhost=False)  # create a manager for handling the MetaDataHub API
    instance_name = mdh_manager.get_instance_name()  # get the instance (core name) of the MetaDataHub request
    mdh_datatypes = mdh_manager.get_datatypes()  # get all mdh_datatypes of the request
    mdh_data = mdh_manager.get_data()  # get all mdh_data from the request

    last_import_timestamp = get_last_import_timestamp()  # Implement your logic to retrieve the last import timestamp from OpenSearch

    data_types = modify_datatypes(mdh_datatypes=mdh_datatypes)  # modify the datatypes so they fit in OpenSearch
    filtered_data = filter_modified_data(mdh_data=mdh_data, data_types=data_types,
                                         last_import_timestamp=last_import_timestamp)  # filter the modified data

    os_manager = OpenSearchManager(localhost=False)  # create a manager for handling the OpenSearch API
    os_manager.create_index(index_name=instance_name, data_types=data_types)  # create an index for the new data
    os_manager.perform_bulk(index_name=instance_name,
                            data=filtered_data)  # perform a bulk request to store the new data in OpenSearch

    print("Finished!")
