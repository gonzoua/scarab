# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementation of 'submit' command
"""

from .base import Base

class Command(Base):
    """Submit new PR"""

    def register(self, subparsers):
        """Register parser for 'submit' command"""
        parser = subparsers.add_parser('submit')
        parser.set_defaults(func=self.run)

    def run(self, args):
        """Implement 'submit' command"""
        print('')
        print('You supplied the following options for submit:', args)
