from opensearchpy import OpenSearch

import mdh_extraction

""" get the data from the MDH by using the mdh_extraction script """
mdh_data_file = mdh_extraction.result
mdh_data_index = mdh_data_file['mdhSearch']['instanceName'].lower()

""" connect to OpenSearch """
host = 'opensearch-node'  # container name of the opensearch node docker container
port = 9200  # port on which the opensearch node runs
auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

""" Create the client with SSL/TLS and hostname verification disabled. """
try:
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )
except BaseException:
    # connection error; send error message
    print("ERROR unable to connect opensearch instance")

""" create  new index with not default settings """
index_name = mdh_data_index  # the index name
index_body = {
    'settings': {
        'index': {
            'number_of_shards': 4
        }
    }
}
if not client.indices.exists(index_name):  # check if index already exists
    response = client.indices.create(index_name, body=index_body)  # create the index in the opensearch node
    print('\nCreating index:')
    print(index_name)

""" get a json test file that was manually extracted from the mdh (just for testing the code) """
# basepath = os.path.dirname(__file__)
# new_path = os.path.join(basepath, 'Test_Data/test_file_1.json')
# print(new_path)
# with open(new_path, 'r') as f:
#     mdh_file = json.load(f)


""" extract metadata from json file """
modified_data_file = {}  # initialize a new json file
# id = 1
for file in mdh_data_file['mdhSearch']['files']:  # loop over all files
    file_name = ''  # initialize variable for file name
    for metadata in file['metadata']:  # loop over all metadata
        modified_data_file[metadata['name']] = metadata['value']  # save each metadata in the new json file
        if metadata['name'] == 'FileName':  # check if metadata is current file name
            file_name = metadata['value']  # save file name
    print(modified_data_file)
    # upload new json to the opensearch node
    # TODO : Modify so that first iot will be checked if file already exists
    response = client.index(
        index=index_name,
        body=modified_data_file,
        # id = id,
        refresh=True
    )

print('\nIndexing document:')
print(response)
