import time
from opensearchpy import OpenSearch
from opensearchpy.exceptions import ConnectionError, NotFoundError, TransportError, RequestError
from enum import Enum
import json


# from helper_class import Operator

class OpenSearchManager:
    """
     Class for managing the connection to OpenSearch and perform simple and advanced search.
     class is a basic skeleton, and you may need to add more methods and functionality based
     on your specific requirements.
     """

    def __init__(self, localhost: bool = False, import_all=True):
        """
        Create a new OpenSearchManager for handling the connection to OpenSearch.

        :param localhost: A boolean variable that defines whether to connect to a local instance or
                          the docker container.
                          If not set to True, it will automatically connect to the docker container.
        """

        self._set_host(localhost)  # set the host for the OpenSearch connection
        self._connect_to_open_search()
        self.import_all = import_all

    def _set_host(self, localhost: bool):
        """ Setting the host for the OpenSearch connection
        :param localhost: A bool variable that defines whether 
        to connect to a local instance or the docker container
        """
        if localhost:
            self._host = 'localhost'  # connection to localhost (testing purposes)
        else:
            self._host = 'opensearch-node'  # connection to docker container
        self._port = 9200

    def _connect_to_open_search(self):
        """ connecting to Opensearch """

        # Create the client with SSL/TLS and hostname verification disabled
        # Port on which the OpenSearch node runs
        auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
        self._client = OpenSearch(
            hosts=[{'host': self._host, 'port': self._port}],  # Host and port to connect with
            http_auth=auth,  # Credentials
            use_ssl=False,  # Disable SSL
            verify_certs=False,  # Disable verification of certificates
            ssl_assert_hostname=False,  # Disable verification of hostname
            ssl_show_warn=False,  # Disable SSL warnings
            retry_on_timeout=True  # Enable the client to reconnect after a timeout
        )

        # Wait until the node is ready before performing an import
        for _ in range(200):
            try:
                self._client.cluster.health(wait_for_status="yellow")  # Make sure the cluster is available
            except ConnectionError:
                time.sleep(2)  # Take a short break to give the OpenSearch node time to be fully set up

    def disconnect(self):
        """
        Disconnects from OpenSearch.

        :return: None
        """
        self._client.close()

    def get_all_indices(self) -> list[str]:
        """
         :rtype: List of index_names contained in the OpenSearch node
           """
        indices = [index for index in self._client.indices.get('*') if
                   index not in ('.kibana_1', '.opensearch-observability')]
        return indices

    def get_all_fields(self, index_name: str) -> list[str]:
        """Get all fields that belong to an index.

        Args:
            index_name (str): The name of the index to look for.

        Returns:
            list[str]: A list of field names of the corresponding index.
        """
        try:
            index_mapping = self._client.indices.get_mapping(index=index_name)
            properties = index_mapping[index_name]["mappings"]["properties"]
            fields = list(properties.keys())

        except Exception as e:
            print(f"Error occurred while retrieving fields for index '{index_name}': {str(e)}")

        return fields

    def get_datatype(self, index_name: str, field_name: str) -> str:
        """Get the datatype of a specific field for a specific index.

         Args:
             field_name (str): The name of the specific field.
             index_name (str): The name of the index in which the field is stored.

         Returns:
             str: A string containing the name of the corresponding datatype.
         """
        try:
            mapping = self._client.indices.get_mapping(index=index_name)
            datatype = mapping[index_name]['mappings']['properties'][field_name]['type']
            return datatype

        except Exception as e:
            print(
                f"Error occurred while retrieving datatype for field '{field_name}' "
                f"in index '{index_name}': {str(e)}")
            return ""

    def field_exists(self, index_name: str, field_name: str) -> bool:
        """Check if a field exists or if at least one document has a value for it.

        Args:
            index_name (str): The name of the index in which the field is being searched.
            field_name (str): The name of the field that is being searched.

        Returns:
            bool: True if the field exists or at least one document has a value for it, False otherwise.
        """
        try:
            query = {
                "query": {
                    "exists": {
                        "field": field_name
                    }
                }
            }
            response = self._client.search(body=query, index=index_name)
            return bool(response['hits']['hits'])

        except Exception as e:
            print(f"Error occurred while checking field '{field_name}' in index '{index_name}': {str(e)}")
            return False

    def get_total_files(self, index_name):
        query = {
            "query": {
                "match_all": {}
            }
        }

        response = self._client.search(
            body=query,
            index=index_name
        )
        return response['hits']['total']['value']

    def create_index(self, index_name: str):
        """Create a new index with non-default settings.

        Args:
            index_name (str): The name of the new index.

        """
        # The body of the new index creation
        index_body = {
            'settings': {
                'index': {
                    'number_of_shards': 4
                }
            },
            'mappings': {
                'properties':
                    {
                        'timestamp': {'type': 'date', "format": "strict_date_hour_minute_second||epoch_millis"},
                    },
            }

        }

        if not self._client.indices.exists(index=index_name):
            # Check if the index already exists
            response = self._client.indices.create(index=index_name, body=index_body)
            if response["acknowledged"]:
                print(f"Index '{index_name}' created successfully.")
            else:
                print(f"Failed to create index '{index_name}'.")

        else:
            print(f"Index '{index_name}' already exists.")

    def update_index(self, index_name: str, data_types: dict) -> any:
        """ This function adds properties (datatypes for fields) to an existing index

        :param index_name: The name of the index that will be updated
        :param data_types: A dictionary containing all fields and their corresponding datatypes
        :return: Returns a OpenSearch response of the index update action
        """
        # create a mapping body for the new properties
        mapping_body = {"properties": {}}

        try:
            # get all existing properties of this index
            response = self._client.indices.get_mapping(index_name)

            for key, datatype in data_types.items():  # iterate over all item pairs in data_types
                # if this field is not already in the properties, add it
                if key not in response[index_name]['mappings']['properties']:
                    if datatype == "date":
                        # Special handling for datetime types
                        property = {"type": datatype, "format": "strict_date_hour_minute_second||epoch_millis"}
                    else:
                        property = {"type": datatype}
                    mapping_body['properties'][key] = property
            return self._client.indices.put_mapping(index=index_name, body=mapping_body)

        except NotFoundError:
            print(f"Index '{index_name}' not found.")
        except KeyError:
            print(f"No mapping found for index '{index_name}.'")

    def perform_bulk(self, index_name: str, data: list[(dict, id)]) -> object:
        """
        Insert multiple documents into OpenSearch via the bulk API.

        :param index_name: The name of the index to which the new data will be added.
        :param data: A list of dictionaries containing the new data and its values in the right format.
        :return: The response of the bulk request.
        """
        create_operation = {
            "create": {"_index": index_name}
        }

        bulk_data = []
        for doc, id in data:
            if not id == "default_id":
                create_operation['create']['_id'] = id
            bulk_data.append(str(create_operation))
            bulk_data.append(str(doc))
        bulk_request = "\n".join(bulk_data).replace("'", "\"")
        try:
            return self._client.bulk(body=bulk_request)
        except TransportError:
            print("Bulk data oversteps the amount of allowed bytes")
            return None

    def add_to_index(self, index_name: str, body: dict, id: int) -> object:
        response = self._client.index(
            index=index_name,
            body=body,
            id=id,
            refresh=True
        )
        return response

    def simple_search(self, index_name: str, search_text: str) -> any:
        """
        A function that performs a simple search in OpenSearch.

        :param index_name: The name of the index in which the search should be performed.
        :param search_text: The search text that will be searched for.
        :return: Returns an OpenSearch response.
        """
        fields = self.get_all_fields(index_name)
        query = {
            "query": {
                "bool": {
                    "should": []
                }
            }
        }
        for field in fields:
            data_type = self.get_datatype(field_name=field, index_name=index_name)
            if data_type == "text":
                sub_query = {"wildcard": {field: {"value": "*" + search_text + "*"}}}
                query['query']['bool']['should'].append(sub_query)

        response = self._client.search(
            body=query,
            index=index_name
        )
        return response

    def advanced_search(self, index_name: str, search_info: dict) -> any:
        """
        Function that performs an advanced search in OpenSearch.

        :param index_name: The name of the index in which the search should be performed.
        :param search_info: A dictionary containing the different fields and operators for
        the advanced search.
        :return: None (or specify the return type if applicable).
        """

        sub_queries = []
        for search_field in search_info:
            print(self.field_exists(index_name, search_field))
            if self.field_exists(index_name, search_field):
                data_type = self.get_datatype(index_name, search_field)
                search_content = search_info[search_field]['search_content']
                operator = search_info[search_field]['operator']
                weight = search_info[search_field]['weight']
                sub_queries.append(self._get_sub_query(data_type, operator, search_field, weight, search_content))
        if sub_queries:
            query = self._get_query(sub_queries)
        else:
            query = {"query": {"exists": {"field": " "}}}
        print("Advanced_query:", query)

        response = self._client.search(
            body=query,
            index=index_name
        )
        return response

    @staticmethod
    def _get_query(sub_queries: list[tuple]) -> dict:
        """
        Function that creates a query that can be used to search in OpenSearch.

        :param sub_queries: A list of tuples that contains the subquery and either
        the value 'must' or 'must_not'.
        :return: Returns a query that can be used to search in OpenSearch.
        """
        # The default size is 10, now it goes to 100 for example!
        query = {'size': 100, 'query': {'bool': {}}}
        for sub_query, functionality in sub_queries:
            if functionality not in query['query']['bool']:
                query['query']['bool'][functionality] = [sub_query]
            else:
                query['query']['bool'][functionality].append(sub_query)
        return query

    @staticmethod
    def _get_sub_query(data_type: str, operator: str, search_field: str, weight: str, search_content: any) -> tuple:
        """Returns a subquery that can be used to create a complete query.

          Args:
              data_type (str): The datatype of the field of the subquery.
              operator (str): The operator of the query.
              search_field (str): The field in which the search should be performed in this subquery.
              search_content (any): The content of the search.

          Returns:
              tuple: A tuple consisting of a subquery and the value 'must' or 'must_not'.

          """
        if data_type == 'float' or data_type == 'date':
            if operator == Operator.IS_EQUAL.value:
                return {'term': {search_field: {'value': search_content, 'boost': weight}}}, 'must'
            elif operator == Operator.IS_GREATER_THAN.value:
                return {'range': {search_field: {'gt': search_content, 'boost': weight}}}, 'must'
            elif operator == Operator.IS_LESS_THAN.value:
                return {'range': {search_field: {'lte': search_content, 'boost': weight}}}, 'must'
            elif operator == Operator.IS_LESS_THAN_OR_EQUAL.value:
                return {'range': {search_field: {'lt': search_content, 'boost': weight}}}, 'must'
            elif operator == Operator.IS_GREATER_THAN_OR_EQUAL.value:
                return {'range': {search_field: {'gte': search_content, 'boost': weight}}}, 'must'
            elif operator == Operator.IS_NOT_EQUAL.value:
                return {'term': {search_field: {'value': search_content, 'boost': weight}}}, 'must_not'
            else:
                return {'term': {search_field: {'value': search_content, 'boost': weight}}}, 'must'
        elif data_type == 'text':
            if operator == Operator.IS_EQUAL.value:
                return {"term": {search_field + ".keyword": {"value": search_content, 'boost': weight}}}, 'must'
            elif operator == Operator.IS_NOT_EQUAL.value:
                return {"wildcard": {search_field: {"value": "*" + search_content + "*", 'boost': weight}}}, 'must_not'
            else:
                return {"wildcard": {search_field: {"value": "*" + search_content + "*", 'boost': weight}}}, 'must'

    def get_latest_timestamp(self, index_name) -> any:
        """
          Retrieves the timestamp of the newest file uploaded to the OpenSearch Node based on the upload date in the MetaDataHub.

          Args:
              index_name (str): The name of the index to search for the timestamp.

          Returns:
              str: The timestamp as a string.

          Raises:
              KeyError: If no data is stored for the specified index.
              NotFoundError: If no index with the given name is found.
              IndexError: If an index error occurs while retrieving the timestamp.
              RequestError: If a request error occurs while retrieving the timestamp.
          """

        query = {
            "size": 1,
            "query": {
                "exists": {
                    "field": "MdHTimestamp"
                },
            },
            "sort": [
                {
                    "MdHTimestamp": "desc"
                }
            ]
        }
        try:
            response = self._client.search(
                body=query,
                index=index_name
            )
            mdh_timestamp = response['hits']['hits'][0]['_source']['MdHTimestamp']
            return mdh_timestamp.replace("T", " ")
        except KeyError:
            print(f"No data for the index '{index_name}' is stored.")
            return False
        except NotFoundError:
            print(f"No index with name '{index_name}' found.")
            return False
        except IndexError:
            return False
        except RequestError:
            return False

    def get_last_import(self, index_name):
        """
        Retrieves the information of the last import from the specified index.

        Args:
            index_name (str): The name of the index from which to retrieve the last import.

        Returns:
            dict: The information of the last import as a dictionary.

        Raises:
            KeyError: If no data is stored for the specified index.
            NotFoundError: If no index with the given name is found.
            IndexError: If an index error occurs while retrieving the last import.
            RequestError: If a request error occurs while retrieving the last import.
        """
        query = {
            "size": 1,
            "query": {
                "exists": {
                    "field": "Version"
                },
            },
            "sort": [
                {
                    "Version": "desc"
                }
            ]
        }
        try:
            response = self._client.search(
                body=query,
                index=index_name
            )
            last_import = response['hits']['hits'][0]['_source']
            return last_import
        except KeyError:
            print(f"No data for the index '{index_name}' is stored.")
            return False
        except NotFoundError:
            print(f"No index with name '{index_name}' found.")
            return False
        except IndexError:
            print(f"Index error for index '{index_name}'")
            return False
        except RequestError:
            print(f"Request error for index '{index_name}'")
            return False


class Operator(Enum):
    """
    Represents different operators for query comparisons.
    """

    IS_EQUAL = 'is_equal'  # Represents the "equals" operator
    IS_NOT_EQUAL = 'is_not_equal'  # Represents the "not equals" operator
    IS_GREATER_THAN = 'is_greater'  # Represents the "greater than" operator
    IS_LESS_THAN = 'is_smaller'  # Represents the "less than" operator
    IS_GREATER_THAN_OR_EQUAL = 'is_greater_or_equal'  # Represents the "greater than or equal to" operator
    IS_LESS_THAN_OR_EQUAL = 'is_smaller_or_equal'  # Represents the "less than or equal to" operator
