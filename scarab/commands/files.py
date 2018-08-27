# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementatoin of the 'files' command
"""

from datetime import datetime, timezone

from ..bugzilla import BugzillaError
from ..context import bugzilla_instance
from .. import ui
from .base import Base

def format_date(date):
    """
    Format date based on current datetime.
    Include year if it's more than a year since the date
    """
    delta = datetime.utcnow().replace(tzinfo=timezone.utc) - date
    if delta.days < 364:
        return date.strftime('%b %d %H:%M')

    return date.strftime('%Y %b %d')


class Command(Base):
    """List files attached to specified PR"""

    def register(self, subparsers):
        parser = subparsers.add_parser('files')
        parser.set_defaults(func=self.run)
        parser.add_argument('bug_id', type=int, help='Bug ID')
        parser.add_argument('-a', '--all', action='store_true', \
            help='show all attachments (including obsolete)')
        parser.add_argument('-s', '--summary', action='store_true', \
            help='show summary instead of file name')

    def run(self, args):
        bugzilla = bugzilla_instance()
        try:
            attachments = bugzilla.attachments(args.bug_id, args.all)
        except BugzillaError as exc:
            ui.fatal('Bugzilla error: {}'.format(exc.message))

        rows = []
        for attachment in attachments:
            row = []
            row.append(str(attachment.object_id))
            row.append(attachment.creator)
            row.append(str(attachment.size))
            row.append(format_date(attachment.creation_time))
            if args.all:
                row.append('O' if attachment.is_obsolete else '')
            row.append(attachment.summary if args.summary else attachment.file_name)
            rows.append(row)

        # find width for every columen except last one
        # it's either file name or summary so should not be limited
        if rows:
            column_formats = []
            for i in range(len(rows[0]) - 1):
                width = max([len(str(row[i])) for row in rows])
                column_format = '{: >%d}' % width
                column_formats.append(column_format)
            row_format = '  '.join(column_formats)
            row_format += ' {}'
            for row in rows:
                ui.output(row_format.format(*row))
