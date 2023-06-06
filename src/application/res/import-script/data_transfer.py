from datetime import datetime
from mdh_api import MetaDataHubManager
import sys
import os

# Get the path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the sys.path list
sys.path.append(parent_dir)

from backend.opensearch_api import OpenSearchManager


def modify_datatypes(mdh_datatypes: dict) -> dict:
    """
    Reformatting the mdh_datatypes dictionary for storage in OpenSearch.

    :param mdh_datatypes: A dictionary containing the corresponding datatypes to the metadata-tags from a MetaDataHub request.
    :return: A dictionary containing the corresponding OpenSearch datatypes for the metadata-tags.
    """
    modified_datatypes = {}  # init the resulting dictionary
    for mdh_datatype in mdh_datatypes:  # loop over all entries of the mdh_datatypes dictionary
        name = mdh_datatype.get("name").replace(".",
                                                "_")  # get the name of the metadata-tag and replace the '.' with '_' to avoid parsing errors
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
    return modified_datatypes


def modify_data(mdh_data: list[dict], data_types: dict) -> list[dict]:
    """
    Reformatting the mdh_data dictionary for storage in OpenSearch.

    :param mdh_data: A list of dictionaries that contains all metadata-tags for every file of a MetaDataHub request.
    :param data_types: A dictionary containing the modified OpenSearch datatypes.
    :return: A list of dictionaries containing the modified metadata tags and their corresponding values.
    """

    modified_data = []  # init the resulting list
    for index, file_data in enumerate(mdh_data, start=1):  # Loop over all files of mdh_data
        metadata = file_data.get("metadata", [])  # get the metadata for each file
        file_info = {}  # init the dictionary in which the metadata will be stored
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


if __name__ == "__main__":
    print("Start importing...")
    mdh_manager = MetaDataHubManager(localhost=False)  # create a manager for handling the MetaDataHub API
    instance_name = mdh_manager.get_instance_name()  # get the instance (core name) of the MetaDataHub request
    mdh_datatypes = mdh_manager.get_datatypes()  # get all mdh_datatypes of the request
    mdh_data = mdh_manager.get_data()  # get all mdh_data from the request
    data_types = modify_datatypes(mdh_datatypes=mdh_datatypes)  # modify the datatypes so they fit in OpenSearch
    data = modify_data(mdh_data=mdh_data, data_types=data_types)  # modify the data so it fits in OpenSearch
    os_manager = OpenSearchManager(localhost=False)  # create a manager for handling the OpenSearch API
    os_manager.create_index(index_name=instance_name, data_types=data_types)  # create an index for the new data
    os_manager.perform_bulk(index_name=instance_name,
                            data=data)  # perform a bulk request to store the new data in OpenSearch
    print("Finished!")
