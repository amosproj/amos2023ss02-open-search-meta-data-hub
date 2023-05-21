import time
import numpy as np
from opensearchpy import OpenSearch, helpers


def get_sample_data():
    response = {
    "data": {
        "mdhSearch": {
            "files": [
                {
                    "metadata": [
                        {
                            "name": "FileName",
                            "value": "which-attributes.gif"
                        },
                        {
                            "name": "FileSize",
                            "value": "44955"
                        },
                        {
                            "name": "MIMEType",
                            "value": "image/gif"
                        },
                        {
                            "name": "FileInodeChangeDate",
                            "value": "2023-03-10 08:28:00"
                        },
                        {
                            "name": "SourceFile",
                            "value": "/media/harvest/general/basic/which-attributes.gif"
                        }
                    ]
                },
                {
                    "metadata": [
                        {
                            "name": "FileName",
                            "value": "HEIC.heic"
                        },
                        {
                            "name": "FileSize",
                            "value": "293608"
                        },
                        {
                            "name": "MIMEType",
                            "value": "image/heif"
                        },
                        {
                            "name": "FileInodeChangeDate",
                            "value": "2023-03-10 08:28:00"
                        },
                        {
                            "name": "SourceFile",
                            "value": "/media/harvest/general/basic/HEIC.heic"
                        }
                    ]
                },
                {
                    "metadata": [
                        {
                            "name": "FileName",
                            "value": "image_0.jpeg"
                        },
                        {
                            "name": "FileSize",
                            "value": "29967"
                        },
                        {
                            "name": "MIMEType",
                            "value": "image/jpeg"
                        },
                        {
                            "name": "FileInodeChangeDate",
                            "value": "2023-03-10 08:28:00"
                        },
                        {
                            "name": "SourceFile",
                            "value": "/media/harvest/general/basic/image_0.jpeg"
                        }
                    ]
                },
                {
                    "metadata": [
                        {
                            "name": "FileName",
                            "value": "image-00041.dcm"
                        },
                        {
                            "name": "FileSize",
                            "value": "86664"
                        },
                        {
                            "name": "MIMEType",
                            "value": "application/dicom"
                        },
                        {
                            "name": "FileInodeChangeDate",
                            "value": "2023-03-10 08:28:00"
                        },
                        {
                            "name": "SourceFile",
                            "value": "/media/harvest/domain/medical_science/dicom/series-00000/image-00041.dcm"
                        }
                    ]
                },
                {
                    "metadata": [
                        {
                            "name": "FileName",
                            "value": "image-00171.dcm"
                        },
                        {
                            "name": "FileSize",
                            "value": "92528"
                        },
                        {
                            "name": "MIMEType",
                            "value": "application/dicom"
                        },
                        {
                            "name": "FileInodeChangeDate",
                            "value": "2023-03-10 08:28:00"
                        },
                        {
                            "name": "SourceFile",
                            "value": "/media/harvest/domain/medical_science/dicom/series-00000/image-00171.dcm"
                        }
                    ]
                },
                {
                    "metadata": [
                        {
                            "name": "FileName",
                            "value": "PPT-Sample-with-Images.pptx"
                        },
                        {
                            "name": "FileSize",
                            "value": "5309683"
                        },
                        {
                            "name": "MIMEType",
                            "value": "application/zip"
                        },
                        {
                            "name": "FileInodeChangeDate",
                            "value": "2023-03-10 08:28:00"
                        },
                        {
                            "name": "SourceFile",
                            "value": "/media/harvest/general/office/PPT-Sample-with-Images.pptx"
                        }
                    ]
                }
            ]
        }
    }
}
    return response

def get_data_format(data_types):
    data_format = {}
    for data_type in data_types:
        name = data_type['name']
        data_format[name] = data_type['type']
    return data_format

def get_client():
    """ connect to OpenSearch """
    host = 'localhost'  # container name of the opensearch node docker container
    port = 9200  # port on which the opensearch node runs
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

    """ Create the client with SSL/TLS and hostname verification disabled. """
    client = OpenSearch(
        hosts=[{'host': host, 'port': port}],  # host and port to connect with
        http_auth=auth,  # credentials
        use_ssl=False,  # disable ssl
        verify_certs=False,  # disable verification of certificates
        ssl_assert_hostname=False,  # disable verification of hostname
        ssl_show_warn=False,  # disable ssl warnings
        retry_on_timeout=True  # enable the client trying to reconnect after a timeout
    )
    return client

def format_output(response):
    mdh_search = response["data"]["mdhSearch"]
    # Extract the relevant information from the data
    files = mdh_search.get("files", [])
    output = []

    # Iterate over the files and extract the required metadata
    for index, file_data in enumerate(files, start=1):
        metadata = file_data.get("metadata", [])
        file_info = {}

        for meta in metadata:
            name = meta.get("name")
            value = meta.get("value")
            if name and value:
                file_info[name] = value

        output.append(file_info)

    return output

def perform_bulk(client: OpenSearch, formated_data: dict, instance_name: str):
    index_operation = {
        "index": {"_index": instance_name}
    }
    create_operation = {
        "create": {"_index": instance_name}
    }
    bulk_data = (str(index_operation) +
                 '\n' + ('\n' + str(create_operation) +
                         '\n').join(str(data) for data in formated_data)).replace("'", "\"")
    client.bulk(bulk_data)

formated_data = format_output(get_sample_data())
bulk_data = perform_bulk(get_client(), formated_data, 'amoscore')




