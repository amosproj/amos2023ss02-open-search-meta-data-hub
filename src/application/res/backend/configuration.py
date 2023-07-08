import configparser


def get_config_values():
    """ sets all configuration values to the specified values defined in config.ini or to their default values

    :return: dictionary containing all options
    """
    # read config file
    config = configparser.ConfigParser()
    config.read('../config.ini')

    # Define fallback and default values
    fallback_values = {
        'localhost': False,
        'index_name': 'amoscore',
        'limit': False,
        'selected_tags': [],
        'only_selected_tags': False
    }

    # Retrieve values from the config file, with fallback to default values
    options = {}
    for key, value in fallback_values.items():
        if key == 'selected_tags':
            options[key] = config.get('General', key, fallback=value).split(";")
        else:
            options[key] = config.get('General', key, fallback=value)


    return options

