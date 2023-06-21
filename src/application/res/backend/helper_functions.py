import configparser

def create_config_parser():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


