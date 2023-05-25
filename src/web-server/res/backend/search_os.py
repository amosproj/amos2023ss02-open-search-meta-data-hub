from opensearchpy import OpenSearch


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

def advanced_search(client: OpenSearch, search_info: dict):
    # This is just a sample idea of how to pass search information from frontend to backend
    search_info = {
        'FileName': {
            'search_content': 'medicine',
            'operator': '=',
            'boost': 2
        },
        'FileSize': {
            'search_content': 500,
            'operator': '>',
            'boost': 2
        },
        'FileNodeChangeDate': '2013-05-05T08:00:00',
        'operator': '>',
        'boost': 3
    }
    query = {}
    return




