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
