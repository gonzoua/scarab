import argparse
import traceback

from importlib import import_module
from pkgutil import walk_packages

import ui

def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="commands", dest="command")
    for entry in walk_packages(__path__, __name__ + '.'):
        try:
            module = import_module(entry[1])
        except Exception as e:
            ui.log("Error importing module '{}': {}".format(entry[1], e))
            ui.log(traceback.format_exc())
            continue

        if hasattr(module, 'Command'):
            command = module.Command()
            command.register(subparsers)
            
    return parser
