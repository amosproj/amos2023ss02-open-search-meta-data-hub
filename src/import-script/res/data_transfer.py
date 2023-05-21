import time
import timeit

from opensearchpy import OpenSearch
from opensearchpy.exceptions import ConnectionError
import mdh_extraction


def get_mdh_data():
    """ get the data from the MDH by using the mdh_extraction script """
    mdh_data = mdh_extraction.result
    instance_name = mdh_data['mdhSearch']['instanceName'].lower()
    return mdh_data, instance_name


def connect_to_os():
    """ connect to OpenSearch """
    host = 'localhost' # container name of the opensearch node docker container
    port = 9200 # port on which the opensearch node runs
    auth = ('admin', 'admin') # For testing only. Don't store credentials in code.

    """ Create the client with SSL/TLS and hostname verification disabled. """
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}], # host and port to connect with
        http_auth=auth, # credentials
        use_ssl=False, # disable ssl
        verify_certs=False, # disable verification of certificates
        ssl_assert_hostname=False, # disable verification of hostname
        ssl_show_warn=False, # disable ssl warnings
        retry_on_timeout=True # enable the client trying to reconnect after a timeout
        )

    """ wait till node is ready before performing an import """
    for _ in range(100):
        try:
            client.cluster.health(wait_for_status="yellow") # make sure the cluster is available
        except ConnectionError:
            time.sleep(2) # take a short break to give the opensearch node time to be fully set-up

    return client


def create_index(client: OpenSearch, mdh_data_index: str):
    """ create  new index with not default settings """
    index_name = mdh_data_index # the index name
    index_body = {
      'settings': {
        'index': {
          'number_of_shards': 4
        }
      }
    }
    if not client.indices.exists(index_name): # check if index already exists
        response = client.indices.create(index_name, body=index_body) # create the index in the opensearch node


def format_data(mdh_data: dict):
    """ reformatting the mdh_data dictionary so it can be stored in OpenSearch """
    mdh_search = mdh_data["mdhSearch"]
    # Extract the relevant information from the data
    files = mdh_search.get("files", [])
    formatted_data = []

    # Iterate over the files and extract the required metadata
    for index, file_data in enumerate(files, start=1):
        metadata = file_data.get("metadata", [])
        file_info = {}
        for meta in metadata:
            name = meta.get("name")
            value = meta.get("value")
            if name and value:
                file_info[name] = value

        formatted_data.append(file_info)

    return formatted_data


def perform_bulk(client: OpenSearch, formatted_data: list, instance_name: str):
    """ inserting multiple documents into opensearch via a bulk API """
    index_operation = {
        "index": {"_index": instance_name}
    }
    create_operation = {
        "create": {"_index": instance_name}
    }
    bulk_data = (str(index_operation) +
                 '\n' + ('\n' + str(create_operation) +
                         '\n').join(str(data) for data in formatted_data)).replace("'", "\"")
    client.bulk(bulk_data)


if __name__ == "__main__":
    start = timeit.timeit()
    print("Start importing...")
    _mdh_data, _instance_name = get_mdh_data()
    _client: OpenSearch = connect_to_os()
    _formatted_data = format_data(_mdh_data)
    perform_bulk(_client, _formatted_data, _instance_name)
    end = timeit.timeit()
    print("Finished, time needed: ", end - start)





