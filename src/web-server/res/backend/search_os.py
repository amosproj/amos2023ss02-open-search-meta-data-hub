from opensearchpy import OpenSearch
import json


def simple_search(client: OpenSearch, search_text):
    query = {
        "query": {
            "match": {
                "FileName": search_text
            }
        }
    }

    response = client.search(
        body=query,
        index='amoscore'
    )
    return response


# To replace the dynamic values in the query string,
# you can use string manipulation methods provided by this method.
#  Here's an example:
def perform_advanced_search(client: OpenSearch, search_info: dict):
    filter_functions = [
        {"field": "FileName", "operator": "EXIST"},
        {"field": "FileName", "operator": "NOT_EXIST"},
        {"field": "FileSize", "operator": "EMPTY"},
        {"field": "FileSize", "operator": "NOT_EMPTY"},
        {"field": "FileName", "operator": "CONTAINS", "value": "example"},
        {"field": "FileName", "operator": "NOT_CONTAINS", "value": "abc"},
        {"field": "MIMEType", "operator": "EQUALS", "value": "text/plain"},
        {"field": "MIMEType", "operator": "NOT_EQUALS", "value": "image/jpeg"},
        {"field": "FileSize", "operator": "GREATER_THAN", "value": 1000},
        {"field": "FileSize", "operator": "LESS_THAN", "value": 2000}
    ]

    selected_tags = [
        "FileName",
        "FileSize",
        "MIMEType",
        "FileInodeChangeDate",
        "SourceFile"
    ]

    limit = 100

    # Convert filter_functions list to JSON string
    filter_functions_json = json.dumps(filter_functions)

    # Construct the query with the updated filter functions, logic option, selected tags, and limit
    query = """
       query {
         mdhSearch(
           filterFunctions: %s
           filterLogicOption: AND
           selectedTags: %s
           limit: %d
         ) {
           totalFilesCount
           returnedFilesCount
           instanceName
           timeZone
           fixedReturnColumnSize
           limitedByLicensing
           queryStatusAsText
           dataTypes {
             name
             type
           }
           files {
             metadata {
               name
               value
             }
           }
         }
       }
     """ % (filter_functions_json, selected_tags, limit)

    # Execute the query and process the response as needed

#     # This is just a sample idea of how to pass search information from frontend to backend
#     search_info = {
#         'FileName': {
#             'search_content': 'medicine',
#             'operator': '=',
#             'boost': 2
#         },
#         'FileSize': {
#             'search_content': 500,
#             'operator': '>',
#             'boost': 2
#         },
#         'FileNodeChangeDate': '2013-05-05T08:00:00',
#         'operator': '>',
#         'boost': 3
#     }
#     query = {}
#     return
