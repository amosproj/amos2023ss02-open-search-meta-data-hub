
from mdh_api import MetaDataHubManager
import time
from import_pipeline import *


mdh_manager = MetaDataHubManager(True)
instance_name = 'amoscore'
latest_timestamp = "1111-11-11 11:11:11"

print(f"Starting to download data from '{instance_name}' in MdH that was added after "
      f"{(latest_timestamp, 'begin')[latest_timestamp == '1111-11-11 11:11:11']}.")
start_time_extracting = time.time()
mdh_manager.download_data(timestamp=latest_timestamp, limit=500000)
mdh_datatypes = mdh_manager.get_datatypes()  # get all mdh_datatypes of the request
mdh_data = mdh_manager.get_data()  # get all mdh_data from the request
files_amount = len(mdh_data)  # amounts of files downloaded from MdH
print(f"--> Finished to download data from MdH!")
print(f"--> {files_amount} files with a total of {len(mdh_datatypes)} metadata-tags have been downloaded.")
print("--> Time needed: %s seconds!" % (time.time() - start_time_extracting))

# Modifying the data into correct format
print("Starting to modify the data.")
start_time_modifying = time.time()
data_types = modify_datatypes(mdh_datatypes=mdh_datatypes)  # modify the datatypes so they fit in OpenSearch
data = modify_data(mdh_data=mdh_data, data_types=data_types)  # modify the data so it fits in OpenSearch
print("--> Finished to modify the data!")
print("--> Time needed: %s seconds!" % (time.time() - start_time_modifying))

dict = {}
for file, id in data:
    for name, value in file.items():
        if name == "FileType":
            if value not in dict:
                dict[value] = len(file)+1
            else:
                if len(file)+1 > dict[value]:
                    dict[value] = len(file)+1


all_tags = []
for name, type in data_types.items():
    all_tags.append(name)

print(all_tags)
print(len(all_tags))



