from configparser import ConfigParser

class Settings(object):
    DEFAULT_CONFIG_FILENAMES = ['~/.scarab']

    def __init__(self):
        pass

    def load(self):
        for filename in DEFAULT_CONFIG_FILENAMES:
            config = ConfigParser()
            config = (filename)
