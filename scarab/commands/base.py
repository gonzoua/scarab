# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Base class for CLI command. All CLI commands are modules in
scarab.commands.* packag and should implement scarab.commands.Base
interface: register and run methods.
"""

class Base(object):
    """A base command."""

    def __init__(self):
        pass

    def register(self, subparsers):
        """
        Creates and registers command parser using add_parser method.
        Should be re-implemented in child class
        """
        raise NotImplementedError('You must implement the register() method yourself!')


    def run(self, args):
        """
        Actual implementation of the command functionality. args is argparse
        params object.
        Should be re-implemented in child class
        """
        raise NotImplementedError('You must implement the run() method yourself!')
