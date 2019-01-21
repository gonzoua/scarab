# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
'update' command implementation'''
"""

from base64 import b64encode
import argparse
import magic

from ..bugzilla import BugzillaError
from ..context import bugzilla_instance

from .. import ui
from .base import Base

class Command(Base):
    """Modify some of the fields of an existing PR"""

    def register(self, subparsers):
        """Register 'update' parser"""
        parser = subparsers.add_parser('update')
        parser.set_defaults(func=self.run)
        parser.add_argument('pr', type=int, help='PR number')
        parser.add_argument('-s', '--status', dest='status', help='new status')
        parser.add_argument('-r', '--resolution', dest='resolution', help='new resolution')
        parser.add_argument('-a', '--assigned-to', dest='assigned_to', help='user to assign PR to')
        parser.add_argument('-C', '--add-cc', dest='add_cc', action='append', help='email to add to Cc (can be specified multiple times)')
        parser.add_argument('-X', '--remove-cc', dest='remove_cc', action='append', help='email to remove from Cc (can be specified multiple times)')
        comment_group = parser.add_mutually_exclusive_group()
        comment_group.add_argument('-c', '--comment', dest='comment', help='comment text')
        comment_group.add_argument('-F', '--comment-file', dest='comment_file', \
            type=argparse.FileType('r'), help='file with comment text')

    def run(self, args):
        """Run 'update' command"""
        bugzilla = bugzilla_instance()

        comment = args.comment
        if comment is None:
            if args.comment_file:
                comment = args.comment_file.read()

        if not (args.status or args.resolution or args.assigned_to \
          or args.add_cc or args.remove_cc or comment):
            ui.fatal('No change specified, at least one of the fields required')

        try:
            attachment = bugzilla.update(args.pr, status=args.status,
              resolution=args.resolution, assigned_to=args.assigned_to,
              add_cc=args.add_cc, remove_cc=args.remove_cc,
              comment=comment)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))
