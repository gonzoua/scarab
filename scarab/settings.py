# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
Representation of scarab's run-time settings
"""

import configparser
import os
import urllib

class Settings(object):
    class TemplateNotFound(Exception):
        def __init__(self, template_name):
            self.template_name = template_name

    """Singleton class that provides access to run-time settings"""
    __instance = None
    VALID_TEMPLATE_KEYS = [
        'product',
        'component',
        'version',
        'severity',
        'platform',
    ]
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
        self.__templates = {}
        # Parse template
        for section in self.__config:
            if not section.startswith('template:'):
                continue
            template_name = section[9:]
            template = {}
            for key in self.__config[section]:
                if not key in self.VALID_TEMPLATE_KEYS:
                    raise Exception("Invalid template key '{}' " \
                        "in section '{}'".format(key, section))
                template[key] = self.__config[section][key]
                self.__templates[template_name] = template

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

    def template(self, name):
        """
        Returns dict with values from template 'name' or raises KeyError
        if it doesn't exist
        """
        if name in self.__templates:
            return self.__templates[name]

        raise self.TemplateNotFound(name)

    def combine_templates(self, names):
        """
        Returns dict with values from template 'name' or None if template
        with such name does not exist
        """
        result = {}
        for name in names:
            template = self.template(name)
            result.update(template)

        return result
