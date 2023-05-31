data_types = {
    'FileName': {"type": "text"},
    'FileSize': {"type": "integer"},
    'MIMEType': {"type": "text","fielddata": True},
    #TODO: Please try to make this work
    # 'FileInodeChangeDate': {
    #     "type": "date",
    #     "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
    # },
    'FileInodeChangeDate': {"type": "text"},
    'SourceFile': {"type": "text"}
}
