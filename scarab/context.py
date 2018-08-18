# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from settings import Settings
from bugzilla import Bugzilla

def settings_instance():
    return Settings()

def bugzilla_instance():
    settings = Settings()
    bugzilla = Bugzilla(settings.url())
    bugzilla.set_api_key(settings.api_key())
    return bugzilla
