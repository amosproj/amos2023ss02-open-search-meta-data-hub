from datetime import datetime
from mdh_api import MetaDataHubManager
import sys
import os

# Get the path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the sys.path list
sys.path.append(parent_dir)

from backend.opensearch_api import OpenSearchManager


def update_last_import_timestamp(timestamp):
    """
    Update the last import timestamp with the provided value.

    :param timestamp: The new timestamp value to be stored as the last import timestamp.
    :return: None
    """
    try:
        with open('last_import_timestamp.txt', 'w') as file:
            file.write(str(timestamp))
    except IOError:
        """
                     with comments to indicate areas that can be discussed with other developers:
             """

        # Handle the case when an error occurs while writing the timestamp file
        # You can choose to raise an exception or handle the error gracefully
        # Example: raise IOError("Error occurred while writing the last import timestamp file")
        print("Error occurred while writing the last import timestamp file")


def load_last_import_timestamp():
    """
    Load the last import timestamp from a file.

    :return: The last import timestamp as a datetime object, or None if it couldn't be loaded.
    """
    try:
        with open('last_import_timestamp.txt', 'r') as file:
            timestamp_str = file.read().strip()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return timestamp
    except FileNotFoundError:
        """
                with comments to indicate areas that can be discussed with other developers:
        """

        # Handle the case when the file doesn't exist
        # Example: return datetime(2023, 1, 1, 0, 0, 0)  # Return a default timestamp
        # Example: raise FileNotFoundError("Last import timestamp file not found")  # Raise an exception
        return None
    except ValueError:
        """
                with comments to indicate areas that can be discussed with other developers:
             """
        # Handle the case when the timestamp format in the file is invalid
        # Example: return datetime(2023, 1, 1, 0, 0, 0)  # Return a default timestamp
        # Example: raise ValueError("Invalid timestamp format in the file")  # Raise an exception
        return None


def modify_datatypes(mdh_datatypes):
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
    return modified_datatypes


def filter_modified_data(mdh_data, data_types, last_import_timestamp):
    """
    Filter and select the data that has been modified or added since the last import.

    :param mdh_data: A list of dictionaries that contains all metadata-tags for every file of a MetaDataHub request.
    :param data_types: A dictionary containing the modified OpenSearch datatypes.
    :param last_import_timestamp: The timestamp of the last import.
    :return: A list of dictionaries containing the modified metadata tags and their corresponding values.
    """
    modified_data = [
        {
            str(meta.get("name")).replace(".", "_"): (
                float(meta.get("value")) if data_types[str(meta.get("name")).replace(".", "_")] == 'float' else
                str(datetime.strptime(meta.get("value"), "%Y-%m-%d %H:%M:%S").utcnow().strftime(
                    "%Y-%m-%d" "T" "%H:%M:%S"))
                if data_types[str(meta.get("name")).replace(".", "_")] == 'date' else
                meta.get("value")
            )
            for meta in file_data.get("metadata", [])
        }
        for file_data in mdh_data
        if file_data.get("timestamp") > last_import_timestamp
    ]

    return modified_data


def transform_data(mdh_data, data_types):
    """
    Transform the mdh_data dictionary for storage in OpenSearch.

    :param mdh_data: A list of dictionaries that contains all metadata-tags for every file of a MetaDataHub request.
    :param data_types: A dictionary containing the modified OpenSearch datatypes.
    :return: A list of dictionaries containing the modified metadata tags and their corresponding values.
    """

    transformed_data = []
    for file_data in mdh_data:
        metadata = file_data.get("metadata", [])
        file_info = {}
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
        transformed_data.append(file_info)

    return transformed_data


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

    # Load the last import timestamp from a file or database
    last_import_timestamp = load_last_import_timestamp()

    mdh_manager = MetaDataHubManager(localhost=False)

    instance_name = mdh_manager.get_instance_name()

    mdh_datatypes = mdh_manager.get_datatypes()
    mdh_data = mdh_manager.get_data()

    data_types = modify_datatypes(mdh_datatypes=mdh_datatypes)

    # Modify the data only for the files that have been modified or added since the last import
    modified_data = modify_data(mdh_data=mdh_data, data_types=data_types, last_import_timestamp=last_import_timestamp)

    os_manager = OpenSearchManager(localhost=False)

    # Check if the index already exists in OpenSearch
    if os_manager.index_exists(index_name=instance_name):
        print("Index already exists. Skipping import.")
    else:
        os_manager.create_index(index_name=instance_name, data_types=data_types)
        os_manager.perform_bulk(index_name=instance_name, data=modified_data)

    # Update the last import timestamp with the current timestamp
    update_last_import_timestamp(datetime.utcnow())

    print("Finished!")
