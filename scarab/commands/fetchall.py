# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementation of fetchall command
"""

import os

from .base import Base
from ..context import bugzilla_instance
from ..bugzilla import BugzillaError
from .. import ui

class Command(Base):
    """Download all non-obsolete attachement for specified bug ID"""

    def register(self, subparsers):
        """Register parser for 'fetchall' command"""
        parser = subparsers.add_parser('fetchall')
        parser.set_defaults(func=self.run)
        parser.add_argument('bug_id', type=int, help='bug ID')

    def run(self, args):
        """Implementation of the 'fetchall' command"""
        bugzilla = bugzilla_instance()
        try:
            attachments = bugzilla.attachments(args.bug_id)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))

        for attachment in attachments:
            file_name = os.path.basename(attachment.file_name)
            orig_file_name = file_name
            # If file exists try to download to filename.N
            i = 1
            while os.path.exists(file_name):
                file_name = orig_file_name + '.' + str(i)
                i += 1

            ui.output("Downloading attachment #{} to {}".format(attachment.object_id, file_name))
            try:
                attachment = bugzilla.attachment(attachment.object_id, data=True)
            except BugzillaError as ex:
                ui.fatal('Bugzilla error: {}'.format(ex.message))

            try:
                out = open(file_name, 'wb+')
                out.write(attachment.data)
            except IOError as ex:
                ui.fatal('error saving file: {}'.format(str(ex)))
