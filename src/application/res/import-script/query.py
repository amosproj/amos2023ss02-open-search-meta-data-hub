import graphene


class MdhSearchQuery(graphene.ObjectType):
    # Define the fields of MdhSearchQuery
    filterFunctions = graphene.String(required=True)
    filterLogicOption = graphene.String()
    selectedTags = graphene.String()
    limit = graphene.String()

    # Setter method for filterFunctions field
    def set_filter_functions(self, value):
        self.filterFunctions = value

    # Getter method for filterFunctions field
    def get_filter_functions(self):
        return self.filterFunctions

    # Setter method for filterLogicOption field
    def set_filter_logic_option(self, value):
        self.filterLogicOption = value

    # Getter method for filterLogicOption field
    def get_filter_logic_option(self):
        return self.filterLogicOption

    # Setter method for selectedTags field
    def set_selected_tags(self, value):
        self.selectedTags = value

    # Getter method for selectedTags field
    def get_selected_tags(self):
        return self.selectedTags

    # Setter method for limit field
    def set_limit(self, value):
        self.limit = value

    # Getter method for limit field
    def get_limit(self):
        return self.limit


class Query(graphene.ObjectType):
    # Define the mdh_search field of the Query object
    mdh_search = graphene.Field(MdhSearchQuery)

    def resolve_mdh_search(self, info):
        # Perform your logic here to retrieve and process the data
        # You can access the input values using `info.variable_values`

        # Retrieve the mdh_search_query input
        mdh_search_query = info.variable_values.get("mdh_search", None)

        # Check if mdh_search_query is provided
        if mdh_search_query:
            # Create a response dictionary with the field values
            response = {
                "filterFunctions": mdh_search_query.get_filter_functions(),
                "filterLogicOption": mdh_search_query.get_filter_logic_option(),
                "selectedTags": mdh_search_query.get_selected_tags(),
                "limit": mdh_search_query.get_limit()
            }
        else:
            # If mdh_search_query is not provided, create a response with an error message
            response = {
                "message": "No input provided for mdh_search query."
            }

        return response


# Create the schema with the Query object
schema = graphene.Schema(query=Query)

# Instantiate the MdhSearchQuery class
mdh_search_query = MdhSearchQuery()

# Set values using the setter methods
mdh_search_query.set_filter_functions("SampleFilterFunction")
mdh_search_query.set_filter_logic_option("AND")
mdh_search_query.set_selected_tags("SampleSelectedTags")
mdh_search_query.set_limit("SampleLimit")

# Retrieve values using the getter methods
filter_functions = mdh_search_query.get_filter_functions()
filter_logic_option = mdh_search_query.get_filter_logic_option()
selected_tags = mdh_search_query.get_selected_tags()
limit = mdh_search_query.get_limit()

# Print the values
print("Filter Functions:", filter_functions)
print("Filter Logic Option:", filter_logic_option)
print("Selected Tags:", selected_tags)
print("Limit:", limit)
