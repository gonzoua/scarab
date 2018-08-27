# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementation of 'fetch' command
"""

import sys
import os

from ..context import bugzilla_instance
from ..bugzilla import BugzillaError
from .. import ui
from .base import Base

class Command(Base):
    """Download attachment specified by ID"""

    def register(self, subparsers):
        """Register args parser for 'fetch' command"""
        parser = subparsers.add_parser('fetch')
        parser.set_defaults(func=self.run)
        parser.add_argument('attachment_id', type=int, help='attachment ID')
        parser.add_argument('-o', '--output', dest='output', \
            help='output filename, use - for stdout')

    def run(self, args):
        """Implementation for 'fetch' command"""
        bugzilla = bugzilla_instance()
        try:
            attachment = bugzilla.attachment(args.attachment_id)
        except BugzillaError as exc:
            ui.fatal('Bugzilla error: {}'.format(exc.message))

        if attachment is None:
            ui.fatal('attachment {} not found'.format(args.attachment_id))

        # Not None and not empty
        if args.output:
            file_name = args.output
        else:
            file_name = os.path.basename(attachment.file_name)
            orig_file_name = file_name
            # If file exists try to download to filename.N
            i = 1
            while os.path.exists(file_name):
                file_name = orig_file_name + '.' + str(i)
                i += 1

        desc_name = 'standard out' if file_name == '-' else file_name
        ui.output("Downloading attachment #{} to {}".format(attachment.object_id, desc_name))
        try:
            attachment = bugzilla.attachment(args.attachment_id, data=True)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))

        try:
            if file_name == '-':
                out = sys.stdout.buffer
            else:
                out = open(file_name, 'wb+')
            out.write(attachment.data)
        except IOError as ex:
            ui.fatal('error saving file: {}'.format(str(ex)))
