from graphql_query import Argument, Operation, Query, Field


class FilterFunction:
    def __init__(self, tag: str, value: str, operation: str, data_type: str):
        """Creates a new object of class FilterFunction.

        Args:
            tag (str): The name of the MdH metadata-tag that this filter function is applied to.
            value (str): The value of the corresponding MdH metadata-tag.
            operation (str): The operation of the filter function, e.g., EQUALS, GREATER, ...
            data_type (str): The datatype of the corresponding metadata-tag.
        """
        self.tag = Argument(name="tag", value=f'"{tag}"')
        self.value = Argument(name="value", value=f'"{value}"')
        self.operation = Argument(name="operation", value=operation)
        self.data_type = Argument(name="dataType", value=data_type)

    def get_filter_function(self) -> list:
        """Returns this filter function as a list for later processing.

        Returns:
            list: List of properties of the filter function.
        """
        return [self.tag, self.value, self.operation, self.data_type]


class SortFunction:
    def __init__(self, tag: str, operation: str = "ASC"):
        """Creates a new object of class SortFunction.

        Args:
            tag (str): The name of the MdH metadata-tag that this sort function is applied to.
            operation (str): The operation of the filter, e.g., EQUALS, GREATER, ...
        """
        self.sort_by = Argument(name="sortBy", value=f'"{tag}"')
        self.sort_by_option = Argument(name="sortByOption", value=operation)

    def get_sort_function(self):
        """Returns this sort function as a list for later processing.

        Returns:
            list: List of properties of the sort function.
        """
        return [self.sort_by, self.sort_by_option]


class GraphQLQuery:
    def __init__(self, filter_functions: list = None, sort_functions: list = None, limit: int = False, filter_logic="AND"):
        """Creates a new object of class GraphQLQuery.

        Args:
            filter_functions (list, optional): List of filter functions to be applied to the GraphQL query. Defaults to [].
            sort_functions (list, optional): List of sort functions to be applied to the GraphQL query. Defaults to [].
            limit (int, optional): Limit that determines the amount of files to be downloaded with the GraphQL query. Defaults to False.
            filter_logic (str, optional): Logic to be used for all filters. Defaults to "AND".
        """
        if filter_functions is None:
            filter_functions = list()
        if sort_functions is None:
            sort_functions = list()
        self.filter_functions = filter_functions
        self.sort_functions = sort_functions
        self.limit = Argument(name="limit", value=limit)
        self.filter_logic = Argument(name="filterLogicOption", value=filter_logic)

    def _get_filter_functions(self) -> Argument:
        """Returns all filter functions as arguments for the GraphQL query.

        Returns:
            graphql_query.Argument: Argument containing all filter functions.
        """
        filter_functions = Argument(
            name="filterFunctions",
            value=[filter.get_filter_function() for filter in self.filter_functions]
        )
        return filter_functions

    def _get_sort_functions(self) -> Argument:
        """Returns all sort functions as arguments for the GraphQL query.

        Returns:
            graphql_query.Argument: Argument containing all sort functions.
        """
        sort_functions = Argument(
            name="sortFunctions",
            value=[s.get_sort_function() for s in self.sort_functions]
        )
        return sort_functions

    def _get_arguments(self, filter_functions: Argument, sort_functions: Argument):
        """Returns all necessary arguments for the GraphQL query.

        Args:
            filter_functions (graphql_query.Argument): Argument containing all filter functions.
            sort_functions (graphql_query.Argument): Argument containing all sort functions.

        Returns:
            list: List of GraphQL query arguments.
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
        """Creates a new GraphQL query in the correct string format by using all the arguments provided to this object.

        Returns:
            str: String containing the GraphQL query.
        """
        # Get all arguments into a list
        filter_functions = self._get_filter_functions()
        sort_functions = self._get_sort_functions()
        arguments = self._get_arguments(filter_functions, sort_functions)

        # Create new query
        query = Query(
            name="mdhSearch",  # Name of the query
            arguments=arguments,  # List of arguments
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
        operation = Operation(type="query", queries=[query])  # Transform query into an operation

        # Return the rendered version of the executed query as a string
        return operation.render()



