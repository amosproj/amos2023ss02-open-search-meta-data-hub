from opensearchpy import OpenSearch
import json
from backend import connection_os


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


def get_datatype(client: OpenSearch, field_name: str) -> str:
    mapping = client.indices.get_mapping(index='amoscore')
    return mapping['amoscore']['mappings']['properties'][field_name]['type']


def advanced_search(client: OpenSearch, search_info):
    sub_queries = []
    for search_field in search_info:
        data_type = get_datatype(client, search_field)
        search_content = search_info[search_field]['search_content']
        operator = search_info[search_field]['operator']
        sub_queries.append(get_sub_query(data_type, operator, search_field, search_content))
    query = get_query(sub_queries)
    print(query)
    response = client.search(
        body=query,
        index='amoscore'
    )
    return response


def get_query(sub_queries: list[tuple]):
    query = {'query': {'bool': {}}}
    for sub_query, functionality in sub_queries:
        if functionality not in query['query']['bool']:
            query['query']['bool'][functionality] = [sub_query]
        else:
            query['query']['bool'][functionality].append(sub_query)
    return query


def get_sub_query(data_type: str, operator: str, search_field: str, search_content: any) -> tuple:
    if data_type == 'integer':
        if operator == 'EQUALS':
            return {'term': {search_field: {'value': int(search_content)}}}, 'must'
        elif operator == 'GREATER_THAN':
            return {'range': {search_field: {'gt': int(search_content)}}}, 'must'
        elif operator == 'LOWER_THAN':
            return {'range': {search_field: {'lt': int(search_content)}}}, 'must'
        elif operator == 'NOT_EQUALS':
            return {'term': {search_field: {'value': int(search_content)}}}, 'must_not'
    elif data_type == 'text':
        if operator == 'EQUALS':
            return {'match': {search_field: search_content}}, 'must'
        elif operator == 'NOT_EQUALS':
            return {'match': {search_field: search_content}}, 'must_not'


# This is just a sample idea of how to pass search information from frontend to backend
search_info = {
    'FileName': {
        'search_content': 'image',
        'operator': 'EQUALS',
    },
    'FileSize': {
        'search_content': 500,
        'operator': 'GREATER_THAN',
    },
}


# The method iterates over the search information and generates the corresponding query clauses
# based on the provided search criteria.
# The resulting query follows the structure required for querying the specified index.
# This method provides a flexible and reusable approach for constructing queries in an OpenSearch environment.
def construct_query(index_name, search_info):
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

    return query


# Usage
index_name = 'your_index_name'
query = construct_query(index_name, search_info)

print(advanced_search(connection_os.connect_to_os(), search_info))
