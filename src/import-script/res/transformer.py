# Replace the 'response' variable with the actual response data from the query
from opensearch import client

response = {

}

# To create a generic method to get the data format based on the provided dataTypes, you can use the following code:
data_types = response


def get_data_format(data_types):
    data_format = {}
    for data_type in data_types:
        name = data_type['name']
        data_format[name] = data_type['type']
    return data_format


# You can call this method by passing the dataTypes list from the response as an argument, like this:
data_types = response['data']['mdhSearch']['dataTypes']
data_format = get_data_format(data_types)


def format_output(data):
    # Check if the necessary fields are present in the data
    if "data" not in data or "mdhSearch" not in data["data"]:
        return "Invalid data format."

    mdh_search = data["data"]["mdhSearch"]

    # Extract the relevant information from the data
    files = mdh_search.get("files", [])
    output = []

    # Iterate over the files and extract the required metadata
    for index, file_data in enumerate(files, start=1):
        metadata = file_data.get("metadata", [])
        file_info = {}

        for meta in metadata:
            name = meta.get("name")
            value = meta.get("value")
            if name and value:
                file_info[name] = value

        # Build the formatted output row
        row = [
            index,
            file_info.get("FileName", ""),
            file_info.get("FileSize", ""),
            file_info.get("MIMEType", ""),
            file_info.get("FileInodeChangeDate", ""),
            file_info.get("SourceFile", "")
        ]

        output.append(row)

    return output


print("#\tFileName\tFileSize\tMIMEType\tFileInodeChangeDate\tSourceFile")
for row in format_output(response):
    print('\t'.join(str(value) for value in row))
bulk_data = []  # Initialize a list to store the bulk data


# a bulk API call in OpenSearch, you can use the client.bulk method.
# Here's an example of how you can modify the code
mdh_data_file = response
index_name = "amoscore"
for file in mdh_data_file['mdhSearch']['files']:
    modified_data_file = {}  # Initialize a new dictionary for each file
    for metadata in file['metadata']:
        modified_data_file[metadata['name']] = metadata['value']

    # Create the bulk action dictionary for indexing the document
    action = {
        '_index': index_name,
        '_source': modified_data_file
    }

    # Append the action to the bulk_data list
    bulk_data.append(action)

# Perform the bulk API call
response = client.bulk(body=bulk_data, refresh=True)

print('\nIndexing documents:')
print(response)
