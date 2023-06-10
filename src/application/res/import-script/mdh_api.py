import json
import os
import pathlib
import mdh
from dotenv import load_dotenv
import graphene


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
        if localhost:
            gql_path = 'request.gql'
        else:
            gql_path = 'import-script/request.gql'
        self._request_path_file = os.path.join(os.getcwd(), gql_path)  # define where to find the GraphQL request

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


    def modify_graphql(self, timestamp):
        filer_function = '{tag: "MdHTimestamp", value: "' + timestamp + '", operation: GREATER, dataType: TS}'
        try:
            with open(self._request_path_file, 'r') as file:
                query = file.read().strip()
                query = query.replace("filterFunctions: []", "filterFunctions [" + str(filer_function) + "]")
                print(query)
            #with open(self._request_path_file, 'w') as file:
                #file.write(query)
                #pass
        except FileNotFoundError:
            raise FileNotFoundError("GraphQL file not found")


    def reset_graphql(self):
        pass

    def download_data(self, timestamp):
        """ download the data from the request and store it """
        for core in mdh.core.main.get():
            self.result = mdh.core.main.execute(core, self._request_path_file)

    def new_data_exists(self) -> bool:
        """check if since last update new data was added in mdh"""
        pass

    def get_instance_name(self) -> str:
        """ get the instance (core name) from the last request """
        return self.result['mdhSearch']['instanceName'].lower()

    def get_data(self) -> list[dict]:
        """ get data from the result-dictionary """
        mdh_search = self.result["mdhSearch"]
        files = mdh_search.get("files", [])
        return files

    def get_datatypes(self, ) -> dict:
        """ get the datatypes of the regarding metadata tags form the result-dictionary"""
        mdh_search = self.result["mdhSearch"]
        data_types = mdh_search.get("dataTypes", [])
        return data_types

mdm = MetaDataHubManager(True)
mdm.modify_graphql("t")