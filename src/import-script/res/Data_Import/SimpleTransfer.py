import json
import mdh
from dotenv import load_dotenv
import os
import pathlib
from opensearchpy import OpenSearch




load_dotenv()

os.environ['MDH_HOME'] = '/WORK_REPO/Data_Import/mdh_home'


request_path_file=os.path.join(os.getcwd(),"request.gql")
print(request_path_file)


mdh.init()
# if(mdh.core.main.get().count>0):
mdh.core.main.add(
url=os.getenv("URL_CORE_1"),
password_user=os.getenv("PW_USER_CORE_1"))
    # )

print(mdh.core.main.get())
# def get_result():
for core in mdh.core.main.get():
    result=mdh.core.main.execute(core,request_path_file)
    print(result)
        # print(f'{core.name} @ {core.url} @ {core.data}')
    with open('my_file_result_om.json', 'w') as f:
         # write the dictionary to the file
        json.dump(result, f,indent=4)
        print(result)

# # connect to OpenSearch
# host = 'localhost'
# port = 9200
# auth = ('admin', 'admin') # For testing only. Don't store credentials in code.
# # ca_certs_path = '/full/path/to/root-ca.pem' # Provide a CA bundle if you use intermediate CAs with your root CA.

# # Create the client with SSL/TLS and hostname verification disabled.
# client = OpenSearch(
#     hosts = [{'host': host, 'port': port}],
#     http_compress = True, # enables gzip compression for request bodies
#     use_ssl = False,
#     verify_certs = False,
#     ssl_assert_hostname = False,
#     ssl_show_warn = False
# )

# # create a new index
# index_name = 'mdh-test-data'
# index_body = {
#   'settings': {
#     'index': {
#       'number_of_shards': 4
#     }
#   }
# }
# #response = client.indices.create(index_name, body=index_body)

# # get the result json file from SimpleImport
# # mdh_file = SimpleImport.result

# # get a json test file that was manually extracted from the mdh
# basepath = os.path.dirname(__file__)
# new_path = os.path.join(basepath, 'Test_Data/test_file_1.json')
# print(new_path)
# with open(new_path, 'r') as f:
#     mdh_file = json.load(f)

# # extract metadata from file
# new_json = {}
# for file in mdh_file['data']['mdhSearch']['files']:
#     for metadata in file['metadata']:
#         new_json[metadata['name']] = metadata['value']
#     print(new_json)
#     # response = client.index(
#     #     index=index_name,
#     #     body=new_json,
#     #     refresh=True
#     # )

