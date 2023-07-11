import configparser


def get_config_values():
    """ sets all configuration values to the specified values defined in config.ini or to their default values

    :return: dictionary containing all options
    """
    # read config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Define fallback and default values
    fallback_values = {
        'localhost': False,
        'index_name': 'amoscore',
        'search_size': 24,
        'limit': False,
        'selected_tags': "FileName;FileSize;FileType;SourceFile",
        'only_selected_tags': False,
        'only_new_data': True,
        'file_types': "",
    }

    # Retrieve values from the config file, with fallback to default values
    options = {}
    for key, value in fallback_values.items():
        if key == 'selected_tags':
            options[key] = config.get('General', key, fallback=value).split(";")
        elif key == 'limit':
            options[key] = config.getint('General', key, fallback=value)
        elif key == 'search_size':
            options[key] = config.getint('General', key, fallback=value)
        elif key == 'localhost':
            options[key] = config.getboolean('General', key, fallback=value)
        elif key == "only_new_data":
            options[key] = config.getboolean('General', key, fallback=value)
        elif key == "only_selected_tags":
            options[key] = config.getboolean('General', key, fallback=value)
        elif key == "file_types":
            tmp = config.get('General',key,fallback=value)
            options[key] = tmp.split(";")
        else:
            options[key] = config.get('General', key, fallback=value)

    return options

