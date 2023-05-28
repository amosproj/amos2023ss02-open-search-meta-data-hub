import time

from opensearchpy import OpenSearch


class OpenSearchManager:

    def __init__(self, localhost: bool = False):
        self._set_host(localhost)  # Container name of the OpenSearch node Docker container
        self._connect_to_open_search()

    def _set_host(self, localhost: bool):
        if localhost:
            self._host = 'localhost'
        else:
            self._host = 'opensearch-node'

    def _connect_to_open_search(self):
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
        for _ in range(100):
            try:
                self._client.cluster.health(wait_for_status="yellow")  # Make sure the cluster is available
            except ConnectionError:
                time.sleep(2)  # Take a short break to give the OpenSearch node time to be fully set up

    def create_index(self, index_name: str, data_types: dict):
        """ create new index with non-default settings """
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
        for key in data_types:
            if data_types[key] == "date":
                property = {"type": data_types[key], "format": "strict_date_hour_minute_second||epoch_millis"}
            else:
                property = {"type": data_types[key]}
            index_body['mappings']['properties'][key] = property

        if not self._client.indices.exists(index=index_name):  # check if index already exists
            response = self._client.indices.create(index=index_name, body=index_body)  # create the index in the OpenSearch node

    def perform_bulk(self, index_name: str, data: list[dict]):
        """ inserting multiple documents into opensearch via a bulk API """
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
        mapping = self._client.indices.get_mapping(index=index_name)
        return mapping[index_name]['mappings']['properties'][field_name]['type']
