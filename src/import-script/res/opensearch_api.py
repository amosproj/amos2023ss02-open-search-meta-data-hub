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
        """ setting the host for the OpenSearch connection
        :param localhost: a bool variable that defines whether to connect to a local instance or the docker container
        """
        if localhost:
            self._host = 'localhost' # connection to localhost (testing purposes)
        else:
            self._host = 'opensearch-node' # connection to docker container

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

    def create_index(self, index_name: str, data_types: dict):
        """ create new index with non-default settings
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
        for key in data_types: # loop over every entry in the datatypes dictionary
            if data_types[key] == "date": # special handling for datetime-types
                property = {"type": data_types[key], "format": "strict_date_hour_minute_second||epoch_millis"}
            else:
                property = {"type": data_types[key]}
            index_body['mappings']['properties'][key] = property # add the fields and corresponding datatypes to the index body

        if not self._client.indices.exists(index=index_name):  # check if index already exists
            response = self._client.indices.create(index=index_name, body=index_body)  # create the index in the OpenSearch node

    def perform_bulk(self, index_name: str, data: list[dict]) -> object:
        """ inserting multiple documents into opensearch via a bulk API
        :param index_name: the index name of the index the new data will be added to
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

    def get_datatype(self, field_name: str, index_name: str) -> str:
        """ return the datatype of a specific field for a specific index
        :param field_name: the name of the specific field
        :param index_name: the name of the index in which the field is stored
        :return: a string containing the name of the corresponding datatype
        """
        mapping = self._client.indices.get_mapping(index=index_name)
        return mapping[index_name]['mappings']['properties'][field_name]['type']

    def get_all_fields(self, index_name: str, is_used: bool = True) -> list[str]:
        # TODO: create a method that is able to get all fields of an index. if is_used == True only the fields that
        #  have assigned values will be returned otherwise every field
        return
