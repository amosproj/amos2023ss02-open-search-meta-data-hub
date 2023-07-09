import json
import os
import pathlib
import subprocess

from graphql_queries import FilterFunction, SortFunction, GraphQLQuery

import mdh
from dotenv import load_dotenv
from pathlib import Path


class MetaDataHubManager:

    def __init__(self, localhost=False):
        """ creating a new MetaDataHubManager for handling the connection to the MetaDataHub
        :param localhost: Bool variable: if true, connect to environment on device, otherwise on docker-container
        """
        MetaDataHubManager._set_environment(localhost)  # set the MetaDataHub environment
        MetaDataHubManager._connect_to_mdh()  # connect to the MetaDataHub
        self._set_request_path(localhost)
        self.result = {}  # dictionary containing the data from the last request

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

    def _generate_query(self, timestamp: str = False, filters: list = None, limit: int = False, offset: int = False, selected_tags: list = None):
        if filters is None:
            filters = []
        filter_functions = []
        sort_functions = [SortFunction(tag="MdHTimestamp", operation="ASC")]
        if timestamp:
            f = FilterFunction(tag="MdhTimestamp", value=timestamp, operation="GREATER", data_type="TS")
            filter_functions.append(f)

        gql_query = GraphQLQuery(filter_functions=filter_functions, sort_functions=sort_functions
                                 , limit=limit, offset=offset, selected_tags=selected_tags)

        self._write_file(self.format_query(gql_query.generate_query()))
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

    def download_data(self, timestamp: str = False, limit: int = False, offset: int = False):
        """ download the data from the request and store it """
        self._generate_query(timestamp, limit=offset, offset=offset)
        for core in mdh.core.main.get():
            self.result = mdh.core.main.execute(core, self._request_path_file)

    def get_instance_name(self) -> str:
        """ get the instance (core name) from the last request

        :return: String containing the name of the instance on which the downloaded was executed
        """
        return self.result['mdhSearch']['instanceName'].lower()

    def get_data(self) -> list[dict]:
        """ get data from the result-dictionary

        :return: list of dictionaries containing all metadata-tags and their values for each file
        """
        mdh_search = self.result["mdhSearch"]
        files = mdh_search.get("files", [])
        return files

    def get_datatypes(self) -> dict:
        """ get the datatypes of the regarding metadata tags form the result-dictionary

        :return: Dictionary containing all metadata-tags and their corresponding datatypes
        """
        mdh_search = self.result["mdhSearch"]
        data_types = mdh_search.get("dataTypes", [])
        return data_types

    def get_total_files_count(self) -> int:
        """ This function get the total amount of files that are stored in the MetaDataHub core
        on which the download was executed

        :return: Integer containing the total files count
        """
        try:
            mdh_search = self.result["mdhSearch"]
            return mdh_search['totalFilesCount']
        except KeyError:
            print("No files found. Please download the data first.")
            return 0

    def get_return_files_count(self) -> int:
        """ This function gets the amount of files that have been downloaded from the MetaDataHub

        :return: Integer containing the returned files count
        """
        try:
            mdh_search = self.result["mdhSearch"]
            return mdh_search["returnedFilesCount"]
        except KeyError:
            print("No files found. Please download the data first.")
            return 0
