import time
from opensearchpy import OpenSearch
from opensearchpy.exceptions import ConnectionError


class OpenSearchManager:
    """
     Class for managing the connection to OpenSearch and perform simple and advanced search.
     class is a basic skeleton, and you may need to add more methods and functionality based
     on your specific requirements.
     """

    def __init__(self, localhost: bool = False):
        """
        Create a new OpenSearchManager for handling the connection to OpenSearch.

        :param localhost: A boolean variable that defines whether to connect to a local instance or
                          the docker container.
                          If not set to True, it will automatically connect to the docker container.
        """

        self._set_host(localhost)  # set the host for the OpenSearch connection
        self._connect_to_open_search()

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

    def get_datatype(self, field_name: str, index_name: str) -> str:
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

    def create_index(self, index_name: str, data_types: dict):
        """Create a new index with non-default settings.

        Args:
            index_name (str): The name of the new index.
            data_types (dict): A dictionary containing all fields and their corresponding data types.

        """
        # The body of the new index creation
        index_body = {
            'settings': {
                'index': {
                    'number_of_shards': 4
                }
            },
            'mappings': {
                'properties': {}
            }
        }

        for key, datatype in data_types.items():
            if datatype == "date":
                # Special handling for datetime types
                property = {"type": datatype, "format": "strict_date_hour_minute_second||epoch_millis"}
            else:
                property = {"type": datatype}
            index_body['mappings']['properties'][key] = property

        if not self._client.indices.exists(index=index_name):
            # Check if the index already exists
            response = self._client.indices.create(index=index_name, body=index_body)
            if response["acknowledged"]:
                print(f"Index '{index_name}' created successfully.")
            else:
                print(f"Failed to create index '{index_name}'.")

        else:
            print(f"Index '{index_name}' already exists.")

    def perform_bulk(self, index_name: str, data: list[dict]) -> object:
        """
        Insert multiple documents into OpenSearch via the bulk API.

        :param index_name: The name of the index to which the new data will be added.
        :param data: A list of dictionaries containing the new data and its values in the right format.
        :return: The response of the bulk request.
        """
        index_operation = {
            "index": {"_index": index_name}
        }
        create_operation = {
            "create": {"_index": index_name}
        }
        bulk_data = (str(index_operation) +
                     '\n' + ('\n' + str(create_operation) +
                             '\n').join(str(d) for d in data)).replace("'", "\"")
        return self._client.bulk(body=bulk_data)

    def simple_search(self, index_name: str, search_text: str) -> any:
        """
        A function that performs a simple search in OpenSearch.

        :param index_name: The name of the index in which the search should be performed.
        :param search_text: The search text that will be searched for.
        :return: Returns an OpenSearch response.
        """

        query = {
            "query": {
                "match": {
                    "FileName": search_text
                }
            }
        }

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

        print("Search_info: ", search_info)
        sub_queries = []
        for search_field in search_info:
            print(self.field_exists(index_name, search_field))
            if self.field_exists(index_name, search_field):
                data_type = self.get_datatype(index_name, search_field)
                search_content = search_info[search_field]['search_content']
                operator = search_info[search_field]['operator']
                sub_queries.append(self._get_sub_query(data_type, operator, search_field, search_content))
        if sub_queries:
            query = self._get_query(sub_queries)
        else:
            query = {"query": {"exists": {"field": " "}}}
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

        query = {'query': {'bool': {}}}
        for sub_query, functionality in sub_queries:
            if functionality not in query['query']['bool']:
                query['query']['bool'][functionality] = [sub_query]
            else:
                query['query']['bool'][functionality].append(sub_query)
        return query

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

    #  data_type = 'float'  # Replace with the actual data type
    # operator = 'GREATER_THAN'  # Replace with the actual operator
    # search_field = 'price'  # Replace with the actual search field
    #  search_content = 100  # Replace with the actual search content

    #  query, query_type = generate_search_query(data_type, operator, search_field, search_content)

    #  usage in an OpenSearch API call
    # result = client.search(index='your_index', body={'query': {query_type: query}})

    @staticmethod
    def _get_sub_query(data_type: str, operator: str, search_field: str, search_content: any) -> tuple:
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
            if operator == 'EQUALS':
                return {'term': {search_field: {'value': search_content}}}, 'must'
            elif operator == 'GREATER_THAN':
                return {'range': {search_field: {'gt': search_content}}}, 'must'
            elif operator == 'LESS_THAN':
                return {'range': {search_field: {'lt': search_content}}}, 'must'
            elif operator == 'GREATER_THAN_OR_EQUALS':
                return {'range': {search_field: {'gte': search_content}}}, 'must'
            elif operator == 'LESS_THAN_OR_EQUALS':
                return {'range': {search_field: {'lte': search_content}}}, 'must'
            elif operator == 'NOT_EQUALS':
                return {'term': {search_field: {'value': search_content}}}, 'must_not'
            else:
                return {'term': {search_field: {'value': search_content}}}, 'must'
        elif data_type == 'text':
            if operator == 'EQUALS':
                return {'match': {search_field: search_content}}, 'must'
            elif operator == 'NOT_EQUALS':
                return {'match': {search_field: search_content}}, 'must_not'
            else:
                return {'match': {search_field: search_content}}, 'must'


# this is just another method optimized
def get_sub_query(self, data_type: str, operator: str, search_field: str, search_content: any) -> tuple:
    """Returns a subquery that can be used to create a complete query.

    Args:
        data_type (str): The datatype of the field of the subquery.
        operator (str): The operator of the query.
        search_field (str): The field in which the search should be performed in this subquery.
        search_content (any): The content of the search.

    Returns:
        tuple: A tuple consisting of a subquery and the value 'must' or 'must_not'.

    """
    sub_query = {}

    if data_type == 'float' or data_type == 'date':
        range_operator_mapping = {
            'EQUALS': 'term',
            'GREATER_THAN': 'range',
            'LESS_THAN': 'range',
            'GREATER_THAN_OR_EQUALS': 'range',
            'LESS_THAN_OR_EQUALS': 'range',
            'NOT_EQUALS': 'term'
        }
        range_operator = range_operator_mapping.get(operator, 'term')

        if range_operator == 'term':
            sub_query = {'term': {search_field: {'value': search_content}}}
        elif range_operator == 'range':
            range_query = {'range': {search_field: {}}}

            if operator == 'GREATER_THAN':
                range_query['range'][search_field]['gt'] = search_content
            elif operator == 'LESS_THAN':
                range_query['range'][search_field]['lt'] = search_content
            elif operator == 'GREATER_THAN_OR_EQUALS':
                range_query['range'][search_field]['gte'] = search_content
            elif operator == 'LESS_THAN_OR_EQUALS':
                range_query['range'][search_field]['lte'] = search_content

            sub_query = range_query

    elif data_type == 'text':
        text_operator_mapping = {
            'EQUALS': 'match',
            'NOT_EQUALS': 'match'
        }
        text_operator = text_operator_mapping.get(operator, 'match')
        sub_query = {text_operator: {search_field: search_content}}

    functionality = 'must' if operator != 'NOT_EQUALS' else 'must_not'
    return sub_query, functionality
