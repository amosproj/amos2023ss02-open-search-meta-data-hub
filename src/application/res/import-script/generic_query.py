def generate_query(filter_tag, filter_value, filter_operation, filter_data_type, limit):
    write_file("request.gql","")
    query = """
        query {
            mdhSearch(
                filterFunctions: [
                    {
                        tag: "%s",
                        value: "%s",
                        operation: %s,
                        dataType: %s
                    }
                ],
                filterLogicOption: AND,
                limit: %d
            ) {
                totalFilesCount
                returnedFilesCount
                instanceName
                timeZone
                fixedReturnColumnSize
                limitedByLicensing
                queryStatusAsText
                dataTypes {
                    name
                    type
                }
                files {
                    metadata {
                        name
                        value
                    }
                }
            }
        }
        """ % (filter_tag, filter_value, filter_operation, filter_data_type, limit)

    write_file("request.gql",query)

    return query


from pathlib import Path


def read_file(file_path):
    path = Path(file_path)
    with path.open(mode='r') as file:
        contents = file.read()
    return contents


def write_file(file_path, contents):
    path = Path(file_path)
    with path.open(mode='w') as file:
        file.write(contents)


def main():
    filter_tag = "MdHTimestamp"
    filter_value = "2023-06-10 15:23:43"
    filter_operation = "EQUAL"
    filter_data_type = "TS"
    limit = 2

    query = generate_query(filter_tag, filter_value, filter_operation, filter_data_type, limit)
    print(query)

    contents = read_file("request.gql")
    print(contents)


if __name__ == "__main__":
    main()
