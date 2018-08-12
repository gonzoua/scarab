import argparse

from importlib import import_module
from pkgutil import walk_packages

def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="commands", dest="command")
    for entry in walk_packages(__path__, __name__ + '.'):
        try:
            module = import_module(entry[1])
        except Exception as e:
            print ('Invalid module', entry[1], e)
            continue

        if hasattr(module, 'Command'):
            command = module.Command()
            command.register(subparsers)
            
    return parser
