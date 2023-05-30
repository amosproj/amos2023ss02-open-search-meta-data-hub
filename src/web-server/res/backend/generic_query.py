from opensearchpy import OpenSearch
from search_os import search_info

# Create a client instance
client = OpenSearch(hosts=['opensearch-node'], port=9200)

# Specify the index name
index_name = 'your_index_name'

# Construct the query
query = {
    'query': {
        'bool': {
            'must': [],
            'filter': []
        }
    }
}

for field, field_info in search_info.items():
    if field == 'operator':
        query['query']['bool'][field] = field_info
        continue

    field_query = {
        'term': {
            field: {
                'value': field_info['search_content'],
                'boost': field_info.get('boost', 1)
            }
        }
    }

    if 'operator' in field_info:
        operator_mapping = {
            '=': 'must',
            '>': 'gt',
            '<': 'lt',
            '>=': 'gte',
            '<=': 'lte'
        }
        operator = operator_mapping.get(field_info['operator'])
        if operator:
            field_query['term'][field].update({operator: field_info['search_content']})

    if field_query:
        query['query']['bool']['must'].append(field_query)

# Execute the search
response = client.search(index=index_name, body=query)

# Process the search results
# ...
