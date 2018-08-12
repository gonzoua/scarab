from json import dumps
from .base import Base

class Command(Base):
    """Submit new PR"""

    def register(self, subparsers):
        parser = subparsers.add_parser('submit')
        parser.set_defaults(func=self.run)

    def run(self, args):
        print ('')
        print ('You supplied the following options for submit:', args)
