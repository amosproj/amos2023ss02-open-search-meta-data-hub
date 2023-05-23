"""All the datatypes that corresponding to the metadata from mdh"""

data_types = {
    'FileName': {"type": "text"},
    'FileSize': {"type": "integer"},
    'MIMEType': {"type": "text"},
    #TODO: Please try to make this work
    # 'FileInodeChangeDate': {
    #     "type": "date",
    #     "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
    # },
    'FileInodeChangeDate': {"type": "text"},
    'SourceFile': {"type": "text"}
}
