# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import magic
from base64 import b64encode
from .base import Base

from context import bugzilla_instance

class Command(Base):
    """Attach file to the existing PR"""

    def register(self, subparsers):
        parser = subparsers.add_parser('attach')
        parser.set_defaults(func=self.run)
        parser.add_argument('pr', type=int, help='PR number')
        parser.add_argument('attachment', type=str, help='path to the attachment')
        parser.add_argument('-s', '--summary', dest='summary', help='summary of the attachment')
        parser.add_argument('-c', '--comment', dest='comment', help='comment text')
        parser.add_argument('-t', '--content-type', dest='content_type', help='file content type')

    def run(self, args):
        bugzilla = bugzilla_instance()
        content_type = args.content_type
        # Read data and encode it to base64
        with open(args.attachment, 'rb') as f:
            data = f.read_all()
            data = b64encode(data)

        # Try and guess file content type
        if content_type is None:
            mime = magic.Magic(mime=True)
            content_type = mime.from_file(args.attachment)
        bugzilla.add_attachment(args.pr, args.attachment, data,
            summary=args.summary, comment=args.comment, content_type=content_type)
