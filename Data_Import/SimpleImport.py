import mdh
import json
from opensearchpy import OpenSearch
from dotenv import load_dotenv
import os


load_dotenv()

request_path_file=os.path.join(os.getcwd(),"request.gql")



mdh.init()

if(mdh.core.main.get().count==0):
    mdh.core.main.add(
    url=os.getenv("URL_CORE_1"),
    password_user=os.getenv("PW_USER_CORE_1")
    )


for core in mdh.core.main.get():
    result=mdh.core.main.execute(core,request_path_file)
    # print(f'{core.name} @ {core.url} @ {core.data}')
    with open('my_file_result.json', 'w') as f:
    # write the dictionary to the file
        json.dump(result, f,indent=4)
        print(result)


# print(result)

host = 'localhost'
port = 9200
auth = ('admin', 'admin') # For testing only. Don't store credentials in code.
# ca_certs_path = '/full/path/to/root-ca.pem' # Provide a CA bundle if you use intermediate CAs with your root CA.

# Optional client certificates if you don't want to use HTTP basic authentication.
# client_cert_path = '/full/path/to/client.pem'
# client_key_path = '/full/path/to/client-key.pem'

# Create the client with SSL/TLS enabled, but hostname verification disabled.
client = OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = auth,
    # client_cert = client_cert_path,
    # client_key = client_key_path,
    use_ssl = False,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
    # ca_certs = ca_certs_path
)

# Create an index with non-default settings.
index_name = 'test-index'
index_body = {
  'settings': {
    'index': {
      'number_of_shards': 4
    }
  }
}

response = client.indices.create(index_name, body=index_body)
print('\nCreating index:')
print(response)

# Add a document to the index.
document = result
id = '1'

response = client.index(
    index = index_name,
    body = document,
    id = id,
    refresh = True
)

print('\nAdding document:')
print(response)

