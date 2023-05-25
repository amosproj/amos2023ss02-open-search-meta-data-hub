from datetime import datetime
from typing import List, Dict, Any

from opensearchpy import OpenSearch

import mdh_extraction
from data_types import data_types


def get_mdh_data() -> tuple:
    """ Get the data from the MDH by using the mdh_extraction script """
    mdh_data = mdh_extraction.result
    instance_name = mdh_data['mdhSearch']['instanceName'].lower()
    return mdh_data, instance_name


def create_index(client: OpenSearch, mdh_data_index: str):
    """ Create a new index with non-default settings """
    index_name = mdh_data_index  # The index name
    index_body = {
        'settings': {
            'index': {
                'number_of_shards': 4
            }
        },
        'mappings': {
            'properties': data_types
        }
    }

    if not client.indices.exists(index_name):  # Check if index already exists
        response = client.indices.create(index_name, body=index_body)  # Create the index in the OpenSearch node
        # Handle the response if needed


def format_data(mdh_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Reformat the mdh_data dictionary so it can be stored in OpenSearch
    """
    mdh_search = mdh_data["mdhSearch"]
    files = mdh_search.get("files", [])
    formatted_data = []

    for file_data in files:
        metadata = file_data.get("metadata", [])
        file_info = {}

        for meta in metadata:
            name = meta.get("name")
            value = meta.get("value")

            # Set correct datatypes
            data_type = get_data_type(name)
            if data_type == 'date':
                value = transform_to_date(value)
            elif data_type == 'integer':
                value = transform_to_integer(value)
            elif data_type == 'list':
                value = transform_to_list(value)
            # Add more transformations for other data types if needed

            if name and value:
                file_info[name] = value

        formatted_data.append(file_info)

    return formatted_data


def perform_bulk(client: OpenSearch, formatted_data: List[dict], instance_name: str):
    """ Insert multiple documents into OpenSearch via a bulk API """
    bulk_data = []
    for data in formatted_data:
        bulk_data.extend([{"index": {"_index": instance_name}}, data])

    client.bulk(bulk_data)


def get_data_type(field: str) -> str:
    """ Get the data type for a given field """
    return data_types.get(field, "text")  # Default to "text" if data type is not defined


def transform_to_date(value: Any) -> Any:
    """
    Transform the value to a date format
    """
    # Add your custom transformation logic here
    transformed_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return transformed_value


def transform_to_integer(value: Any) -> Any:
    """
    Transform the value to an integer
    """
    # Add your custom transformation logic here
    transformed_value = int(value)
    return transformed_value


def transform_to_list(value: Any) -> Any:
    """
    Transform the value to a list
    """
    # Add your custom transformation logic here
    transformed_value = value.split(',')  # Assuming the value is a comma-separated string
    return transformed_value
