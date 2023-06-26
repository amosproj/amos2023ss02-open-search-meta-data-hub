import os
import sys
import time
# Get the path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the sys.path list
sys.path.append(parent_dir)
from backend.opensearch_api import OpenSearchManager

INDEX_NAME = "import_control"

def create_import_index(os_manager: OpenSearchManager):
    fields = {
        'Version': 'integer',
        'Status': 'text',
        'Files to be uploaded': 'text',
        'Successfully uploaded files': 'float',
        'Total files in index': 'integer'
    }
    os_manager.create_index(index_name=INDEX_NAME)
    os_manager.update_index(index_name=INDEX_NAME, data_types=fields)


def save_initial_import(os_manager: OpenSearchManager, files_count):
    if INDEX_NAME not in os_manager.get_all_indices():
        create_import_index(os_manager)
    last_import = os_manager.get_last_import(index_name=INDEX_NAME)
    if last_import:
        last_version = last_import['Version']
        total_files = last_import['Total files in index']
        version = last_version + 1
    else:
        version = 1
        total_files = 0
    id = str(version)
    data = {
             'Version': version,
             'Status': 'Incomplete',
             'Files to be uploaded': files_count,
             'Successfully uploaded files': 0,
             'Total files in index': total_files
         }
    os_manager.add_to_index(index_name=INDEX_NAME, body=data, id=id)



def update_import(os_manager: OpenSearchManager, files_count, uploaded_files):
    time.sleep(5)
    last_import = os_manager.get_last_import(index_name=INDEX_NAME)
    print(last_import)
    if last_import:
        last_version = last_import['Version']
        total_files = last_import['Total files in index']
        id = str(last_version)
        print(files_count, uploaded_files)

        if files_count == uploaded_files:
            status = 'Successful'
        else:
            status = 'Failed'

        data = {
            'Version': last_version,
            'Status': status,
            'Files to be uploaded': files_count,
            'Successfully uploaded files': uploaded_files,
            'Total files in index': total_files + uploaded_files
        }
        os_manager.add_to_index(index_name=INDEX_NAME, body=data, id=id)
        return data


def get_last_import_status(os_manager: OpenSearchManager):
    last_import = os_manager.get_last_import(index_name=INDEX_NAME)
    if last_import:
        status = last_import['Status']
        if status == "Successful":
            return True
        else:
            return False
    else:  # there is no last import
        return False
