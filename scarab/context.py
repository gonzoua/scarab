# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
CLI execution context module. Handles data that can
be accessed by multiple components during CLI lifecycle
e.g.: settings, Bugzilla XMLRPC client.
"""

from .settings import Settings
from .bugzilla import Bugzilla

def settings_instance():
    """Returns Settings singleton"""
    return Settings()

def bugzilla_instance():
    """Creates and returns Bugzilla XMLRPC client"""
    settings = Settings()
    bugzilla = Bugzilla(settings.url())
    bugzilla.set_api_key(settings.api_key())
    return bugzilla
