from graphql_query import Argument, Operation, Query, Field


class FilterFunction:

    def __init__(self, tag: str, value: str, operation: str, data_type: str):
        """ Creates a new object of class FilterFunction
        :param tag: the name of the MdH metadata-tag that this filter function is applied to
        :param value: the value of the corresponding MdH metadata-tag
        :param operation: the operation of the filter function, e.g. EQUALS, GREATER, ...
        :param data_type: the datatype of the corresponding metadata-tag
        """
        self.tag = Argument(name="tag", value=f'"{tag}"')
        self.value = Argument(name="value", value=f'"{value}"')
        self.operation = Argument(name="operation", value=operation)
        self.data_type = Argument(name="dataType", value=data_type)

    def get_filter_function(self) -> list:
        """ This function returns this filter function as a list for later processing
        :return: list of properties of filter function
        """
        return [self.tag, self.value, self.operation, self.data_type]


class SortFunction:

    def __init__(self, tag: str, operation: str):
        """ Creates a new object of class SortFunction
        :param tag: the name of the MdH metadata-tag that this sort function is applied to
        :param operation: the operation of the filter, e.g. EQUALS, GREATER, ...
        """
        self.tag = Argument(name="tag", value=f'"{tag}"')
        self.operation = Argument(name="operation", value=operation)

    def get_sort_function(self):
        """ This function returns this sort function as a list for later processing
        :return: list of properties of sort function
        """
        return [self.tag, self.operation]


class GraphQLQuery:

    def __init__(self, filter_functions: list = [], sort_functions: list = [], limit: int = False, filter_logic="AND"):
        """ Creates a new object of  class GraphQLQuery
        :param filter_functions: a list of filter functions that will be applied to this GraphQL query
        :param sort_functions: a list of sort functions that will be applied to this GraphQL query
        :param limit: a limit that determines the amount of files that will be downloaded with this GraphQL query
        :param filter_logic: the logic that will be used for all filters
        """
        self.filter_functions = filter_functions
        self.sort_functions = sort_functions
        self.limit = Argument(name="limit", value=limit)
        self.filter_logic = Argument(name="filterLogicOption", value=filter_logic)

    def _get_filter_functions(self) -> Argument:
        """ This functions returns all filter functions as arguments for the GraphQL query
        :return: graphql_query Argument containing all filter functions
        """
        filter_functions = Argument(
            name="filterFunctions",
            value=[filter.get_filter_function() for filter in self.filter_functions]
        )
        return filter_functions

    def _get_sort_functions(self) -> Argument:
        """ This functions returns all sort functions as arguments for the GraphQL query
        :return: graphql_query Argument containing all sort functions
        """
        sort_functions = Argument(
            name="sortFunctions",
            value=[s.get_sort_function() for s in self.sort_functions]
        )
        return sort_functions

    def _get_arguments(self, filter_functions: Argument, sort_functions: Argument):
        """ This functions returns all necessary arguments for the GraphQl query
        :param filter_functions: graphql_query Argument containing all sort functions
        :param sort_functions: graphql_query Argument containing all filter functions
        :return: graphql_query Argument
        """
        arguments = [
            filter_functions,
            sort_functions,
            self.filter_logic
        ]
        if self.limit.value:
            arguments.append(self.limit)

        return arguments

    def generate_query(self) -> str:
        """ This functions creates a new graphql in the correct String format by using all the arguments provided to
        this object
        :return: String containing the graphQl query
        """

        # get all arguments into a list
        filter_functions = self._get_filter_functions()
        sort_functions = self._get_sort_functions()
        arguments = self._get_arguments(filter_functions, sort_functions)

        # create new query
        query = Query(
            name="mdhSearch", # name of query
            arguments=arguments, # list of arguments
            # all fields of this query
            fields=[
                "totalFilesCount",
                "returnedFilesCount",
                "instanceName",
                "timeZone",
                "fixedReturnColumnSize",
                "limitedByLicensing",
                "queryStatusAsText",
                Field(name="dataTypes", fields=["name", "type"]),
                Field(
                    name="files",
                    fields=[Field(name="metadata", fields=["name", "value"])]
                )
            ]
        )
        operation = Operation(type="query", queries=[query]) # transform query into an operation

        # return the rendered version of the executed query as string
        return operation.render()


f = FilterFunction("MdhTimestamp", "1", "GREATER", "TS")

q = GraphQLQuery(filter_functions=[f])

print(q.generate_query())
