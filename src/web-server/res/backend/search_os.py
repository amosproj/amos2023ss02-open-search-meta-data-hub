from opensearchpy import OpenSearch
import json
from backend import connection_os


def simple_search(client: OpenSearch, search_text) -> any:
    """ A function that performs a simple search in OpenSearch.
    :param client: OpenSearch client that connects to the OpenSearch node
    :param search_text: The search text that will be searched for
    :return: returns an OpenSearch response
    """
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
    """ Function that returns the datatype to a specific field in OpenSearch
    :param client: OpenSearch client that connects to the OpenSearch node
    :param field_name: The name of the field the datatype is wished for
    :return: returns the name of the datatype of the field
    """
    mapping = client.indices.get_mapping(index='amoscore')
    return mapping['amoscore']['mappings']['properties'][field_name]['type']


def advanced_search(client: OpenSearch, search_info: dict) -> any:
    """ Function that performs an advanced search in OpenSearch
    :param client: OpenSearch client that connects to the OpenSearch node
    :param search_info: a dictionary containing the different fields and operators for the advanced search
    :return:
    """
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


def get_query(sub_queries: list[tuple]) -> dict:
    """ Function that creates a query that can be used to sesrch in OpenSearch
    :param sub_queries: a list of tuples that contains the sub query and either the value must or must_not
    :return: retuns a query that can be used to search in OpenSearch
    """
    query = {'query': {'bool': {}}}
    for sub_query, functionality in sub_queries:
        if functionality not in query['query']['bool']:
            query['query']['bool'][functionality] = [sub_query]
        else:
            query['query']['bool'][functionality].append(sub_query)
    return query


def get_sub_query(data_type: str, operator: str, search_field: str, search_content: any) -> tuple:
    """ Function that returns a subquery thsat can be used to create a complete query
    :param data_type: the datatype of the field of the subquery
    :param operator: the operator of the query
    :param search_field: the field in which should be searched in this suquery
    :param search_content: the content of the search
    :return: returns a tuple consisting of a subquery and either the value must or must_not
    """
    if data_type == 'float' or data_type == 'date':
        if operator == 'EQUALS':
            return {'term': {search_field: {'value': search_content}}}, 'must'
        elif operator == 'GREATER_THAN':
            return {'range': {search_field: {'gt': search_content}}}, 'must'
        elif operator == 'LOWER_THAN':
            return {'range': {search_field: {'lt': search_content}}}, 'must'
        elif operator == 'GREATER_THAN_OR_EQUALS':
            return {'range': {search_field: {'gte': search_content}}}, 'must'
        elif operator == 'LOWER_THAN_OR_EQUALS':
            return {'range': {search_field: {'lte': search_content}}}, 'must'
        elif operator == 'NOT_EQUALS':
            return {'term': {search_field: {'value': search_content}}}, 'must_not'
        else:
            return {'term': {search_field: {'value': search_content}}}, 'must'
    elif data_type == 'text':
        if operator == 'EQUALS':
            return {'match': {search_field: search_content}}, 'must'
        elif operator == 'NOT_EQUALS':
            return {'match': {search_field: search_content}}, 'must_not'
        else:
            return {'match': {search_field: search_content}}, 'must'





