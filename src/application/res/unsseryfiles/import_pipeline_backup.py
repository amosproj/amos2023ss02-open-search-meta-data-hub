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
        # Handle the case when an error occurs while writing the timestamp file
        # You can choose to raise an exception or handle the error gracefully
        # Example: raise IOError("Error occurred while writing the last import timestamp file")
        print("Error occurred while writing the last import timestamp file")


def load_last_import_timestamp() -> str:
    """
    Load the last import timestamp from a file.

    :return: The last import timestamp as a datetime object, or None if it couldn't be loaded.
    """
    try:
        with open('last_import_timestamp.txt', 'r') as file:
            timestamp_str = file.read().strip()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return str(timestamp)
    except FileNotFoundError:
        raise FileNotFoundError("Last import timestamp file not found")
    except ValueError:
        raise ValueError("Invalid timestamp format in the file")


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

    def generate_search_query(data_type, operator, search_field, search_content):
        """
        Generate a search query based on the given parameters.

        :param data_type: The data type of the search field ('float', 'date', or 'text').
        :param operator: The operator for the search query ('EQUALS', 'GREATER_THAN', 'LESS_THAN', 'GREATER_THAN_OR_EQUALS',
                         'LESS_THAN_OR_EQUALS', or 'NOT_EQUALS').
        :param search_field: The field to search within.
        :param search_content: The content to search for.
        :return: A dictionary representing the search query and a flag indicating whether it is a must or must_not condition.
        """

        query_type = 'must'
        query = {}

        if data_type == 'float' or data_type == 'date':
            range_operators = {
                'EQUALS': 'term',
                'GREATER_THAN': 'gt',
                'LESS_THAN': 'lt',
                'GREATER_THAN_OR_EQUALS': 'gte',
                'LESS_THAN_OR_EQUALS': 'lte',
                'NOT_EQUALS': 'term'
            }
            query_type = 'must_not' if operator == 'NOT_EQUALS' else 'must'
            query = {
                range_operators.get(operator, 'term'): {
                    search_field: {'value': search_content}
                }
            }
        elif data_type == 'text':
            query = {
                'match': {
                    search_field: search_content
                }
            }

        return query, query_type


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

def generate_mdh_search_query(filter_functions=None, limit=2000):
    """
    Generate a dynamic MDH search query.

    :param filter_functions: Optional list of filter functions.
    :param limit: Limit on the number of files to return.
    :return: Generated query string.
    """
    query = """
    query {
        mdhSearch(
            filterFunctions: FILTER_FUNCTIONS
            limit: LIMIT
        ) {
            TOTAL_FILES_COUNT
            RETURNED_FILES_COUNT
            INSTANCE_NAME
            TIME_ZONE
            FIXED_RETURN_COLUMN_SIZE
            LIMITED_BY_LICENSING
            QUERY_STATUS_AS_TEXT
            dataTypes {
                NAME
                TYPE
            }
            files {
                metadata {
                    NAME
                    VALUE
                }
            }
        }
    }
    """

    # Replace the placeholders with the provided values
    query = query.replace("FILTER_FUNCTIONS", filter_functions or "[]")
    query = query.replace("LIMIT", str(limit))

    # Convert all keys to uppercase and replace in the query
    query = query.replace("TOTAL_FILES_COUNT", "totalFilesCount")  # Replace key for total files count
    query = query.replace("RETURNED_FILES_COUNT", "returnedFilesCount")  # Replace key for returned files count
    query = query.replace("INSTANCE_NAME", "instanceName")  # Replace key for instance name
    query = query.replace("TIME_ZONE", "timeZone")  # Replace key for time zone
    query = query.replace("FIXED_RETURN_COLUMN_SIZE", "fixed")

def generate_query(filter_tag, filter_value, filter_operation, filter_data_type, limit):
    write_file("request.gql","")
    query = """
        query {
            mdhSearch(
                filterFunctions: [
                    {
                        tag: "%s",
                        value: "%s",
                        operation: %s,
                        dataType: %s
                    }
                ],
                filterLogicOption: AND,
                limit: %d
            ) {
                totalFilesCount
                returnedFilesCount
                instanceName
                timeZone
                fixedReturnColumnSize
                limitedByLicensing
                queryStatusAsText
                dataTypes {
                    name
                    type
                }
                files {
                    metadata {
                        name
                        value
                    }
                }
            }
        }
        """ % (filter_tag, filter_value, filter_operation, filter_data_type, limit)

    write_file("request.gql",query)

    return query


from pathlib import Path


def read_file(file_path):
    path = Path(file_path)
    with path.open(mode='r') as file:
        contents = file.read()
    return contents


def write_file(file_path, contents):
    path = Path(file_path)
    with path.open(mode='w') as file:
        file.write(contents)


def main():
    filter_tag = "MdHTimestamp"
    filter_value = "2023-06-10 15:23:43"
    filter_operation = "EQUAL"
    filter_data_type = "TS"
    limit = 2

    query = generate_query(filter_tag, filter_value, filter_operation, filter_data_type, limit)
    print(query)

    contents = read_file("request.gql")
    print(contents)


if __name__ == "__main__":
    main()


# example of usage
# query_string = generate_mdh_search_query(filter_functions=["your", "filter", "functions"], limit=500)
# print(query_string)
