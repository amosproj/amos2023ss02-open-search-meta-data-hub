import time
from opensearchpy import OpenSearch
from opensearchpy.exceptions import ConnectionError


class OpenSearchManager:

    def __init__(self, localhost: bool = False):
        """ creating a new OpenSearchManager for handling the connection to OpenSearch
        :param localhost: a bool variable that defines whether to connect to a local instance or the docker container. If not set to true it will automatically connect to the docker-container
        """
        self._set_host(localhost)  # set the host for the OpenSearch connection
        self._connect_to_open_search()

    def _set_host(self, localhost: bool):
        """ Setting the host for the OpenSearch connection
        :param localhost: A bool variable that defines whether to connect to a local instance or the docker container
        """
        if localhost:
            self._host = 'localhost'  # connection to localhost (testing purposes)
        else:
            self._host = 'opensearch-node'  # connection to docker container

    def _connect_to_open_search(self):
        """ connecting to Opensearch """

        # Create the client with SSL/TLS and hostname verification disabled
        port = 9200  # Port on which the OpenSearch node runs
        auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
        self._client = OpenSearch(
            hosts=[{'host': self._host, 'port': port}],  # Host and port to connect with
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

    def get_all_indices(self) -> list[str]:
        """
        :rtype: List of index_names contained in the OpenSearch node
        """
        indices = []
        for index in self._client.indices.get('*'):
            if not str(index) == '.kibana_1' and not str(index) == '.opensearch-observability':
                indices.append(index)
        return indices

    def get_all_fields(self, index_name: str) -> list[str]:
        """ Get all field that belong to an index
        :param index_name: The name of the index that is looked for
        :return: Returns a list of field names of the corresponding index
        """
        fields = []
        fields_mapping = self._client.indices.get_mapping(index_name)
        for field in fields_mapping[index_name]["mappings"]["properties"]:
            fields.append(field)
        return fields

    def get_datatype(self, field_name: str, index_name: str) -> str:
        """ Get the datatype of a specific field for a specific index
        :param field_name: The name of the specific field
        :param index_name: The name of the index in which the field is stored
        :return: A string containing the name of the corresponding datatype
        """
        mapping = self._client.indices.get_mapping(index=index_name)
        return mapping[index_name]['mappings']['properties'][field_name]['type']

    def field_exists(self, index_name: str, field_name: str) -> bool:
        """ Function checks if a field exists or at least one document has a value for it
        :param index_name: The name of the index in which is looked for the field
        :param field_name: The name of the field that is been looked for
        :return: returns true if the field exists or at least one document has a value for it or false otherwise
        """
        print(field_name)
        query = {
            "query": {
                "exists": {
                    "field": field_name
                }
            }
        }
        response = self._client.search(
            body=query,
            index=index_name
        )
        return bool(response['hits']['hits'])

    def create_index(self, index_name: str, data_types: dict):
        """ Create new index with non-default settings
        :param index_name: the name of the new index
        :param data_types: a dictionary containing all fields and corresponding datatypes that should be added to the new index
        """
        # the body of the new index creation
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
        for key in data_types:  # loop over every entry in the datatypes dictionary
            if data_types[key] == "date":  # special handling for datetime-types
                property = {"type": data_types[key], "format": "strict_date_hour_minute_second||epoch_millis"}
            else:
                property = {"type": data_types[key]}
            index_body['mappings']['properties'][
                key] = property  # add the fields and corresponding datatypes to the index body

        if not self._client.indices.exists(index=index_name):  # check if index already exists
            response = self._client.indices.create(index=index_name,
                                                   body=index_body)  # create the index in the OpenSearch node

    def perform_bulk(self, index_name: str, data: list[dict]) -> object:
        """ Inserting multiple documents into opensearch via a bulk API
        :param index_name: The  name of the index the new data will be added to
        :param data: a list of dictionaries containing all new data and its values in the right format
        :return: returns the response of the bulk request
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
        """ A function that performs a simple search in OpenSearch.
        :param index_name: The name of the index in which the search should be performed in
        :param search_text: The search text that will be searched for
        :return: returns an OpenSearch response
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
        """ Function that performs an advanced search in OpenSearch
        :param index_name: the name of the index in which the search should be performed in
        :param search_info: a dictionary containing the different fields and operators for the advanced search
        :return:
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
        """ Function that creates a query that can be used to sesrch in OpenSearch
        :param sub_queries: a list of tuples that contains the sub query and either the value must or must_not
        :return: returns a query that can be used to search in OpenSearch
        """
        query = {'query': {'bool': {}}}
        for sub_query, functionality in sub_queries:
            if functionality not in query['query']['bool']:
                query['query']['bool'][functionality] = [sub_query]
            else:
                query['query']['bool'][functionality].append(sub_query)
        return query

    @staticmethod
    def _get_sub_query(data_type: str, operator: str, search_field: str, search_content: any) -> tuple:
        """ Function that returns a subquery that can be used to create a complete query
        :param data_type: the datatype of the field of the subquery
        :param operator: the operator of the query
        :param search_field: the field in which should be searched in this suquery
        :param search_content: the content of the search
        :return: returns a tuple consisting of a subquery and either the value must or must_not
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

