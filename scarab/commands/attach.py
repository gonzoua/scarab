# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
'attach' command implementation'''
"""

from base64 import b64encode

import magic
from ..bugzilla import BugzillaError
from ..context import bugzilla_instance

from .. import ui
from .base import Base

class Command(Base):
    """Attach file to the existing PR"""

    def register(self, subparsers):
        """Register 'attach' parser"""
        parser = subparsers.add_parser('attach')
        parser.set_defaults(func=self.run)
        parser.add_argument('attachment', type=str, help='path to the attachment')
        parser.add_argument('pr', type=int, help='PR number')
        parser.add_argument('-s', '--summary', dest='summary', help='summary for the attachment')
        parser.add_argument('-c', '--comment', dest='comment', help='comment text')
        parser.add_argument('-t', '--content-type', dest='content_type', help='file content type')

    def run(self, args):
        """Run 'attach' command"""
        bugzilla = bugzilla_instance()
        content_type = args.content_type
        # Read data and encode it to base64
        try:
            with open(args.attachment, 'rb') as attach_file:
                data = attach_file.read()
        except IOError as ex:
            ui.fatal('error reading file: {}'.format(str(ex)))

        comment = args.comment
        if comment is None:
            comment = ui.edit_message()

        # Try and guess file content type
        if content_type is None:
            mime = magic.Magic(mime=True)
            content_type = mime.from_file(args.attachment)
        try:
            attachment = bugzilla.add_attachment(args.pr, args.attachment, data, \
                summary=args.summary, comment=comment, content_type=content_type)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))
        ui.output('New attachment {} has been added to bug {}'.format(attachment, args.pr))
        ui.output('Attachment URL: {}'.format(bugzilla.attachment_url(attachment)))
        ui.output('Bug URL: {}'.format(bugzilla.bug_url(args.pr)))
