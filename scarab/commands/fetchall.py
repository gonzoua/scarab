# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import sys
import os
from context import bugzilla_instance

from .base import Base

class Command(Base):
    """Download all non-obsolete attachement for specified bug ID"""

    def register(self, subparsers):
        parser = subparsers.add_parser('fetchall')
        parser.set_defaults(func=self.run)
        parser.add_argument('bug_id', type=int, help='bug ID')

    def run(self, args):
        bugzilla = bugzilla_instance()
        attachments = bugzilla.attachments(args.bug_id)
        for attachment in attachments:
            file_name = os.path.basename(attachment.file_name)
            orig_file_name = file_name
            # If file exists try to download to filename.N
            i = 1
            while os.path.exists(file_name):
                file_name = orig_file_name + '.' + str(i)
                i += 1

            print ("Downloading attachment #{} to {}".format(attachment.object_id, file_name))
            attachment = bugzilla.attachment(attachment.object_id, data=True)
            out = open(file_name, 'wb+')
            out.write(attachment.data)
