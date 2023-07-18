import json
import os
import pathlib
import subprocess

from graphql_queries import FilterFunction, SortFunction, GraphQLQuery

import mdh
from dotenv import load_dotenv
from pathlib import Path


class MetaDataHubManager:
    """
     Class for managing the connection to the MetaDataHub and extract data from it.
     class is a basic skeleton, and you may need to add more methods and functionality based
     on your specific requirements.
     """

    def __init__(self, localhost=False):
        """ creating a new MetaDataHubManager for handling the connection to the MetaDataHub
        :param localhost: Bool variable: if true, connect to environment on device, otherwise on docker-container
        """
        MetaDataHubManager._set_environment(localhost)  # set the MetaDataHub environment
        MetaDataHubManager._connect_to_mdh()  # connect to the MetaDataHub
        self._set_request_path(localhost)
        self.metadata_tags = {}  # dictionary containing the most frequently used metadata tags from the last request
        self.data = {}  # dictionary containing the data from the last request

    def _set_request_path(self, localhost: bool):
        """ Tbhis function initally sets the path to the graphQL file needed for the download from the MetaDataHub

        :param localhost: bool variable for local execution that determines the path of the GraphQl file
        """
        if localhost:
            gql_path = 'request.gql'
        else:
            gql_path = '/WORK_REPO/import-script/request.gql'
        self._request_path_file = gql_path  # os.path.join(os.getcwd(), gql_path)  # define where to find the GraphQL request

    @staticmethod
    def _set_environment(localhost: bool):
        """ set the environment and tell the manager where to find the .env file containing the credentials
        :param localhost: Bool variable: if true, connect to environment on device, otherwise on docker-container
        """
        load_dotenv()  # load the environment
        if localhost:
            env_path = str(pathlib.Path(__file__).parents[1])
            os.environ['MDH_HOME'] = env_path  # set the path to the .env file
        else:
            os.environ['MDH_HOME'] = '/WORK_REPO/mdh_home'  # set the path to the .env file

    @staticmethod
    def _connect_to_mdh():
        """ connect to a MetaDataHub instance (core) """
        try:
            mdh.init()  # initialize a mdh instance
            # add a new mdh core
            mdh.core.main.add(
                url=os.getenv("URL_CORE_1"),
                password_user=os.getenv("PW_USER_CORE_1")
            )
        except mdh.errors.MdhStateError:  # if a connection already exists
            print("Core already exists")

    def _read_file(self) -> str:
        """ This function reads a local GraphQl file

        :return: String containing the file input
        """
        path = Path(self._request_path_file)
        with path.open(mode='r') as file:
            contents = file.read()
        return contents

    def _write_file(self, contents):
        """ This functions writes to a local GraphQl file

        :param contents: the content that will be written into the file
        """
        path = Path(self._request_path_file)
        with path.open(mode='w') as file:
            file.write(contents)

    def _generate_metadata_tag_query(self, amount_of_tags: int = 900):
        """ This function generates a GraphQl query to extract a certain amount of the most used metadata tags

        :param amount_of_tags: amount of metadata tags to be extracted (default = 900)
        :return: returns a GraphQL query string containing the created query based on the settings
        """
        gql_query = GraphQLQuery(amount_of_tags=amount_of_tags)

        self._write_file(self.format_query(gql_query.generate_tag_query()))
        return gql_query

    def _generate_data_query(self, timestamp: str = False, filters: list = None, limit: int = False,
                             offset: int = False, selected_tags: list = None, file_type: str = False):
        """ This function generates a GraphQl query to extract a certain amount of files

        :param timestamp: timestamp of last data extraction. if given only data that was added after this date gets extracted (default = false --> no time filter)
        :param filters: filters to filter the GraphQL query (default = None --> no filters)
        :param limit: limit that determines the amount of files that will be extracted (default = false --> no limit)
        :param offset: offset that determines how many of the first values of the extraction get skipped (default = false --> no offset)
        :param selected_tags: list of tags that will extracted (default = None --> all possible tags get extracted)
        :param file_type: type of file (e.g. xml, jpeg, ...). Only files of this type will be extracted (default = false --> all file types)
        :return: returns a GraphQL query string containing the created query based on the settings
        """
        filter_functions = []
        if timestamp:
            f = FilterFunction(tag="MdHTimestamp", value=timestamp, operation="GREATER", data_type="TS")
            filter_functions.append(f)

        if selected_tags:
            if "SourceFile" not in selected_tags:
                selected_tags.append("SourceFile")

        if file_type:
            t = FilterFunction(tag="FileType", value=file_type, operation="EQUAL", data_type="STR")
            filter_functions.append(t)

        sort_functions = [
            SortFunction(tag="MdHTimestamp", operation="ASC"),
            SortFunction(tag="FileName", operation="ASC")
        ]

        gql_query = GraphQLQuery(filter_functions=filter_functions, sort_functions=[]
                                 , limit=limit, offset=offset, selected_tags=selected_tags)

        self._write_file(self.format_query(gql_query.generate_data_query()))
        return gql_query

    def format_query(self, gql_query: str) -> str:
        """ Formats the query in a readable format

        :param gql_query: the original GraphQl query
        :return: String containing the formatted query
        """
        lines = gql_query.strip().split('\n')
        min_indentation = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
        formatted_query = '\n'.join(line[min_indentation:] for line in lines)
        return formatted_query

    def download_metadata_tags(self, amount_of_tags: int = 900):
        """ download the metadata tags from a request and store it
        :param amount_of_tags: amount of metadata tags to be extracted (default = 900)
        """
        self._generate_metadata_tag_query(amount_of_tags=amount_of_tags)
        for core in mdh.core.main.get():
            self.metadata_tags = mdh.core.main.execute(core, self._request_path_file)

    def download_data(self, timestamp: str = False, limit: int = False, offset: int = False, selected_tags: list = None,
                      file_type: str = False):
        """ download the data from a request and store it
        :param timestamp: timestamp of last data extraction. if given only data that was added after this date gets extracted (default = false --> no time filter)
        :param limit: limit that determines the amount of files that will be extracted (default = false --> no limit)
        :param offset: offset that determines how many of the first values of the extraction get skipped (default = false --> no offset)
        :param selected_tags: list of tags that will extracted (default = None --> all possible tags get extracted)
        :param file_type: type of file (e.g. xml, jpeg, ...). Only files of this type will be extracted (default = false --> all file types)
        """
        self._generate_data_query(timestamp=timestamp, limit=limit, offset=offset, selected_tags=selected_tags,
                                  file_type=file_type)
        for core in mdh.core.main.get():
            self.data = mdh.core.main.execute(core, self._request_path_file)

    def get_instance_name(self) -> str:
        """ get the instance (core name) from the last request

        :return: String containing the name of the instance on which the downloaded was executed
        """
        return self.data['mdhSearch']['instanceName'].lower()

    def get_data(self) -> list[dict]:
        """ get data from the data-dictionary

        :return: list of dictionaries containing all metadata-tags and their values for each file
        """
        try:
            mdh_search = self.data["mdhSearch"]
            files = mdh_search.get("files", [])
            return files
        except KeyError:
            return None

    def get_metadata_tags(self) -> dict:
        """ get the datatypes of the regarding metadata tags form the data-dictionary

        :return: List of dictionaries containing all metadata-tags and their corresponding datatypes
        """
        try:
            mdh_search = self.metadata_tags["getMetadataTags"]
            return mdh_search
        except KeyError:
            return None

    def get_total_files_count(self) -> int:
        """ This function get the total amount of files that are stored in the MetaDataHub core
        on which the download was executed

        :return: Integer containing the total files count
        """
        try:
            mdh_search = self.data["mdhSearch"]
            return mdh_search['totalFilesCount']
        except KeyError:
            print("No files found. Please download the data first.")
            return 0

    def get_return_files_count(self) -> int:
        """ This function gets the amount of files that have been downloaded from the MetaDataHub

        :return: Integer containing the returned files count
        """
        try:
            mdh_search = self.data["mdhSearch"]
            return mdh_search["returnedFilesCount"]
        except KeyError:
            print("No files found. Please download the data first.")
            return 0
