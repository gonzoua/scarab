# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import configparser
import os

class Settings(object):
    __instance = None
    def __new__(cls):
        if Settings.__instance is None:
            Settings.__instance = object.__new__(cls)
            home = os.path.expanduser('~')
            config_file = os.path.join(home, '.scarabrc')
            Settings.__instance.load_file(config_file)
 
        return Settings.__instance

    def load_file(self, path):
        self.__config = configparser.ConfigParser()
        self.__config.read(path)

    def url(self):
        return self.__config['global']['bugzilla']

    def api_key(self):
        return self.__config['global']['api_key']
