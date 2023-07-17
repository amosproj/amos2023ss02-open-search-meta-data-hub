import configparser


def get_config_values():
    """Sets all configuration values to the specified values defined in config.ini or their default values.

    :return: Dictionary containing all options.
    """
    # Helper function to handle boolean values
    def get_boolean_option(section, key, fallback):
        if config.has_option(section, key):
            return config.getboolean(section, key)
        else:
            return fallback

    # Read config file
    config = configparser.ConfigParser()
    config.read('./config.ini')

    # Define fallback and default values
    fallback_values = {
        'localhost': True,
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
        elif key == 'limit' or key == 'search_size':
            options[key] = config.getint('General', key, fallback=value)
        elif key == 'localhost' or key == 'only_new_data' or key == 'only_selected_tags':
            options[key] = get_boolean_option('General', key, fallback=value)
        elif key == 'file_types':
            options[key] = config.get('General', key, fallback=value).split(";")
        else:
            options[key] = config.get('General', key, fallback=value)

    return options
