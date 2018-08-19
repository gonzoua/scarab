# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import sys
import os
from context import bugzilla_instance

from .base import Base

class Command(Base):
    """Download attachment specified by ID"""

    def register(self, subparsers):
        parser = subparsers.add_parser('fetch')
        parser.set_defaults(func=self.run)
        parser.add_argument('attachment_id', type=int, help='attachment ID')
        parser.add_argument('-o', '--output', dest='output', help='output filename, use - for stdout')

    def run(self, args):
        bugzilla = bugzilla_instance()
        attachment = bugzilla.attachment(args.attachment_id)
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
        print ("Downloading attachment #{} to {}".format(attachment.object_id, desc_name))
        attachment = bugzilla.attachment(args.attachment_id, data=True)
        if file_name == '-':
            out = sys.stdout.buffer
        else:
            out = open(file_name, 'wb+')
        out.write(attachment.data)
