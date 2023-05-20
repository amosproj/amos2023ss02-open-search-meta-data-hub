import time

from opensearchpy import OpenSearch
from opensearchpy.exceptions import ConnectionError

import mdh_extraction

""" get the data from the MDH by using the mdh_extraction script """
mdh_data_file = mdh_extraction.result
mdh_data_index = mdh_data_file['mdhSearch']['instanceName'].lower()


""" connect to OpenSearch """
host = 'opensearch-node' # container name of the opensearch node docker container
port = 9200 # port on which the opensearch node runs
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
    print('\nCreating index:')
    print(index_name)



""" extract metadata from json file """
modified_data_file = {} # initialize a new json file
# id = 1
for file in mdh_data_file['mdhSearch']['files']: # loop over all files
    file_name = '' # initialize variable for file name
    for metadata in file['metadata']: # loop over all metadata
        modified_data_file[metadata['name']] = metadata['value'] # save each metadata in the new json file
        if metadata['name'] == 'FileName': # check if metadata is current file name
            file_name = metadata['value'] # save file name
    print(modified_data_file)
    # upload new json to the opensearch node
    #TODO : Modify so that first iot will be checked if file already exists
    response = client.index(
        index=index_name,
        body=modified_data_file,
        # id = id,
        refresh=True
    )

print('\nIndexing document:')
print(response)


