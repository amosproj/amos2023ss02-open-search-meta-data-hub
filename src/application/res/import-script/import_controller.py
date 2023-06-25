import os
import sys


# Get the path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the sys.path list
sys.path.append(parent_dir)
from backend.opensearch_api import OpenSearchManager


def create_import_index(os_manager: OpenSearchManager, index_name: str):
    fields = {
        'Version': 'int',
        'Timestamp': 'date',
        'Status': 'text',
        'Files to be uploaded': 'text',
        'Successfully uploaded files': 'float',
        'Total files in index': 'int'
    }
    os_manager.create_index(index_name=index_name)
    os_manager.update_index(index_name=index_name, data_types=fields)


def save_initial_import(os_manager: OpenSearchManager, index_name, timestamp, files_count):
    last_import = os_manager.get_last_import(index_name=index_name)
    if last_import:
        last_version = last_import['Version']
        total_files = last_import['Total files in index']
        version = last_version+1
    else:
        version = 1
        total_files = 0
    id = version
    data = [({
        'Version': version,
        'Timestamp': timestamp,
        'Status': 'Incomplete',
        'Files to be uploaded': files_count,
        'Successfully uploaded files': 0,
        'Total files in index': total_files
    }, id)]
    os_manager.perfrom_bulk(index_name=index_name, data=data)


def update_import(os_manager: OpenSearchManager, index_name, files_count, uploaded_files):
    last_import = os_manager.get_last_import(index_name=index_name)
    if last_import:
        last_version = last_import['Version']
        total_files = last_import['Total files in index']
        timestamp = last_import['Timestamp']
        id = last_version
        if files_count == uploaded_files:
            status = 'Successful'
        else:
            status = 'Failed'

        data = [({
            'Version': last_version,
            'Timestamp': timestamp,
            'Status': status,
            'Files to be uploaded': files_count,
            'Successfully uploaded files': uploaded_files,
            'Total files in index': total_files + uploaded_files
        }, id)]
        os_manager.perfrom_bulk(index_name=index_name, data=data)
        if status == 'Successful':
            return True
        else:
            return False


def get_last_import_status(os_manager: OpenSearchManager, index_name):
    last_import = os_manager.get_last_import(index_name=index_name)
    if last_import:
        status = last_import['Status']
        if status == "Successful":
            return True
        else:
            return False
    else: # there is no last import
        return False



