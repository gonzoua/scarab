# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Top-level CLI command package
"""
import argparse
import traceback

from importlib import import_module
from pkgutil import walk_packages

from .. import ui

def create_parser():
    """
    Autoload all available modules in the package and check if they're
    command implementation.
    Returns:
        argparse.ArgumentParser object with all available subcommands
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', dest='config', help='config file')
    subparsers = parser.add_subparsers(title="commands", dest="command")
    for entry in walk_packages(__path__, __name__ + '.'):
        try:
            module = import_module(entry[1])
        except Exception as exc:
            ui.log("Error importing module '{}': {}".format(entry[1], exc))
            ui.log(traceback.format_exc())
            continue

        if hasattr(module, 'Command'):
            command = module.Command()
            command.register(subparsers)

    return parser
