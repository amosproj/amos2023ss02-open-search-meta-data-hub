import json
import os
import pathlib
import time
from opensearchpy import OpenSearch
from opensearchpy.exceptions import ConnectionError


""" connect to OpenSearch """
host = 'opensearch-node' # container name of the opensearch node docker container
port = 9200 # port on which the opensearch node run s
auth = ('admin', 'admin') # For testing only. Don't store credentials in code.


""" Create the client with SSL/TLS and hostname verification disabled. """
client = OpenSearch(
    hosts = [{'host': host, 'port': port}], # host and port to connect with
    http_auth=auth, # credentials
    use_ssl=False, # disable ssl
    verify_certs=False, # disable verification of certificates
    ssl_assert_hostname=False, # disable verification of hostname
    ssl_show_warn=False, # disable ssl warnings
    retry_on_timeout=True # enable the client trying to reconnect after a timeout
    )

""" wait till node is ready before performing an import """
print('\nConnection to OpenSearch Node ...')
for _ in range(100):
    try:
        client.cluster.health(wait_for_status="yellow") # make sure the cluster is available
    except ConnectionError:
        time.sleep(2) # take a short break to give the opensearch node time to be fully set-up
print('\nSuccessfully connected!')

""" create a new index with not default settings """
index_name = 'mdh-test-data' # the index name
index_body = {
  'settings': {
    'index': {
      'number_of_shards': 4
    }
  }
}
response = client.indices.create(index_name, body=index_body) # create the index in the opensearch node
print('\nCreating index:')
print(response)


""" get a json test file that was manually extracted from the mdh """
basepath = os.path.dirname(__file__)
new_path = os.path.join(basepath, 'Test_Data/test_file_1.json')
print(new_path)
with open(new_path, 'r') as f:
    mdh_file = json.load(f)


""" extract metadata from json file """
new_json = {} # initialize a new json file
# id = 1
for file in mdh_file['data']['mdhSearch']['files']: # loop over all files
    for metadata in file['metadata']: # loop over all metadata
        new_json[metadata['name']] = metadata['value'] # save each metadata in the new json file
    print(new_json)
    # upload new json to the opensearch node
    response = client.index(
        index=index_name,
        body=new_json,
        # id = id,
        refresh=True
    )

print('\nIndexing document:')
print(response)

