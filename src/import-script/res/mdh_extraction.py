import json
import mdh
from dotenv import load_dotenv
import os
import pathlib


""" init MDH directory """
load_dotenv()
os.environ['MDH_HOME'] = '/WORK_REPO/mdh_home'


""" create the path where to search for data"""
request_path_file=os.path.join(os.getcwd(),"request.gql")

""" Intitialization of the MDH-Core"""
mdh.init()
# if(mdh.core.main.get().count>0):

""" Connecion to MDH-Core """
mdh.core.main.add(
url=os.getenv("URL_CORE_1"),
password_user=os.getenv("PW_USER_CORE_1")
)

""" get a json file with sample-data from the metadata-hub """
result = {}
for core in mdh.core.main.get():
    result = mdh.core.main.execute(core, request_path_file)
