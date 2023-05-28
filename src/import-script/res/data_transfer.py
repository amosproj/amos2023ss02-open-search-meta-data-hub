from datetime import datetime

from mdh_api import MetaDataHubManager
from opensearch_api import OpenSearchManager


def modify_datatypes(mdh_datatypes: dict) -> dict:
    modified_datatypes = {}
    for mdh_datatype in mdh_datatypes:
        name = mdh_datatype.get("name").replace(".", "_")
        type = mdh_datatype.get("type")
        if type == 'num':
            modified_datatypes[name] = 'float'
        elif type == 'ts':
            modified_datatypes[name] = 'date'
        elif type == 'str':
            modified_datatypes[name] = 'text'
        else:
            modified_datatypes[name] = 'text'
    return modified_datatypes


def modify_data(mdh_data: list[dict], data_types) -> list[dict]:
    """ reformatting the mdh_data dictionary so it can be stored in OpenSearch """
    modified_data = []
    # Iterate over the files and extract the required metadata
    for index, file_data in enumerate(mdh_data, start=1):
        metadata = file_data.get("metadata", [])
        file_info = {}
        for meta in metadata:
            name = str(meta.get("name")).replace(".", "_")
            value = meta.get("value")
            # set correct datatypes
            if data_types[name] == 'date':
                date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                #value = date.strftime('%Y-%m-%dT%H:%M:%S')
                value = str(date.utcnow().strftime("%Y-%m-%d" "T" "%H:%M:%S"))
            elif data_types[name] == 'float':
                value = float(value)
            if name and value:
                file_info[name] = value

        modified_data.append(file_info)

    return modified_data


if __name__ == "__main__":
    print("Start importing...")
    mdh_manager = MetaDataHubManager()
    instance_name = mdh_manager.get_instance_name()
    mdh_datatypes = mdh_manager.get_datatypes()
    mdh_data = mdh_manager.get_files()
    data_types = modify_datatypes(mdh_datatypes=mdh_datatypes)
    print(data_types)
    data = modify_data(mdh_data=mdh_data, data_types=data_types)
    print(len(data_types))
    #print(data_types)
    #print(data)
    os_manager = OpenSearchManager(localhost=False)
    #os_manager.create_index(index_name=instance_name, data_types=data_types)
    response = os_manager.perform_bulk(index_name=instance_name, data=data)
    print(response)

    print("Finished!")
