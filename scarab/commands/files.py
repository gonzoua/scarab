from json import dumps
from .base import Base

class Command(Base):
    """Attach file to the existing PR"""

    def register(self, subparsers):
        parser = subparsers.add_parser('files')
        parser.set_defaults(func=self.run)
        parser.add_argument('pr', type=int, help='PR number')
        parser.add_argument('-a', '--all', action='store_true', help='show all attachments (including obsolete)')

    def run(self, args):
        print ('')
        print ('You supplied the following options for attach:', args)
