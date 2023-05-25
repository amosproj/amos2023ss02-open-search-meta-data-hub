from opensearchpy import OpenSearch
import random
from . import connection_os


def fetch_all_MIMEType(client: OpenSearch, index_name):
    query = {
        "aggs": {
            "mime_type_counts": {
                "terms": {
                    "field": "MIMEType",
                    "size": 10
                    }
                }
            }
        }

    try:
        response = client.search(
            body=query,
            index=index_name,
            size=100  # Set an appropriate size to retrieve more documents if necessary
        )
        return response
    except Exception as e:
        print("Error:", e)
        return None

def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    color_code = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    return color_code

def get_files_type():
    client = connection_os.connect_to_os()
    if client:
      data = fetch_all_MIMEType(client=client, index_name="amoscore")
      result=data["aggregations"]["mime_type_counts"]["buckets"]
      keys = [item['key'] for item in result]
      doc_count = [item['doc_count'] for item in result]
      random_colors = [generate_random_color() for _ in range(len(result))]
      return keys,doc_count,random_colors