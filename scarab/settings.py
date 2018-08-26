# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
Representation of scarab's run-time settings
"""

import configparser
import os
import urllib

class Settings(object):
    """Singleton class that provides access to run-time settings"""
    __instance = None
    def __new__(cls):
        if Settings.__instance is None:
            Settings.__instance = object.__new__(cls)
            home = os.path.expanduser('~')
            config_file = os.path.join(home, '.scarabrc')
            Settings.__instance.load_file(config_file)

        return Settings.__instance

    def load_file(self, path):
        """Load ini file specified by path"""
        self.__config = configparser.ConfigParser()
        self.__config.read(path)

    def url(self):
        """
        Returns bugzilla base URL configured in [global]
        section of the config file (parameter 'bugzilla')
        """
        base = self.__config.get('default', 'url', \
            fallback='https://bugs.freebsd.org/bugzilla/')
        if not base.endswith('/'):
            base += '/'
        return urllib.parse.urljoin(base, 'xmlrpc.cgi')

    def api_key(self):
        """
        Returns API key configured in [global] sectoin of
        the config file (parameter 'api_key')
        """
        return self.__config.get('default', 'api_key', fallback=None)
