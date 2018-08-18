from context import bugzilla_instance

from json import dumps
from .base import Base

class Command(Base):
    """Attach file to the existing PR"""

    def register(self, subparsers):
        parser = subparsers.add_parser('files')
        parser.set_defaults(func=self.run)
        parser.add_argument('bug_id', type=int, help='Bug ID')
        parser.add_argument('-a', '--all', action='store_true', help='show all attachments (including obsolete)')

    def run(self, args):
        bugzilla = bugzilla_instance()
        print (bugzilla.attachments(args.bug_id))
