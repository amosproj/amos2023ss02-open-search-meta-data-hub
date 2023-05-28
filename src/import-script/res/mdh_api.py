import os

import mdh
from dotenv import load_dotenv


class MetaDataHubManager:

    def __init__(self):
        """ create the path where to search for data"""
        self._request_path_file = os.path.join(os.getcwd(), "request.gql")
        MetaDataHubManager._set_environment()
        MetaDataHubManager._connect_to_mdh()
        self.result = {}
        self._download_data()

    @staticmethod
    def _set_environment():
        """ set the environment"""
        load_dotenv()
        os.environ['MDH_HOME'] = '/WORK_REPO/mdh_home'

    @staticmethod
    def _connect_to_mdh():
        try:
            """ Connecting to the MDH-Core"""
            mdh.init()  # initialize a mdh instance
            # add a new mdh core
            mdh.core.main.add(
                url=os.getenv("URL_CORE_1"),
                password_user=os.getenv("PW_USER_CORE_1")
            )
        except mdh.errors.MdhStateError:
            print("Core already exists")

    def _download_data(self):
        """ get a json file with sample-data from the metadata-hub """
        for core in mdh.core.main.get():
            self.result = mdh.core.main.execute(core, self._request_path_file)

    def get_instance_name(self) -> str:
        """ get the data from the MDH by using the mdh_extraction script """
        return self.result['mdhSearch']['instanceName'].lower()

    def get_files(self) -> list[dict]:
        """ get files from the result """
        mdh_search = self.result["mdhSearch"]
        files = mdh_search.get("files", [])
        return files

    def get_datatypes(self, ) -> dict:
        """ get the datatypes of the regarding metadata tags"""
        mdh_search = self.result["mdhSearch"]
        # Extract the relevant information from the data
        data_types = mdh_search.get("dataTypes", [])

        return data_types
