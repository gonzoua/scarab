# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from context import bugzilla_instance

from json import dumps
from .base import Base
from datetime import datetime, timezone
from bugzilla import BugzillaError

import ui

class Command(Base):
    """List files attached to specified PR"""

    def register(self, subparsers):
        parser = subparsers.add_parser('files')
        parser.set_defaults(func=self.run)
        parser.add_argument('bug_id', type=int, help='Bug ID')
        parser.add_argument('-a', '--all', action='store_true', help='show all attachments (including obsolete)')
        parser.add_argument('-s', '--summary', action='store_true', help='show summary instead of file name')

    def __format_date(self, date):
        delta =  datetime.utcnow().replace(tzinfo=timezone.utc) - date
        if delta.days < 364:
            return date.strftime('%b %d %H:%M')
        else:
            return date.strftime('%Y %b %d')

    def run(self, args):
        bugzilla = bugzilla_instance()
        try:
            attachments = bugzilla.attachments(args.bug_id, args.all)
        except BugzillaError as e:
            ui.fatal('Bugzilla error: {}'.format(e.message))

        rows = []
        for a in attachments:
            row = []
            row.append(str(a.object_id))
            row.append(a.creator)
            row.append(str(a.size))
            row.append(self.__format_date(a.creation_time))
            if args.all:
                row.append('O' if a.is_obsolete else '')
            row.append(a.summary if args.summary else a.file_name)
            rows.append(row)

        # find width for every columen except last one
        # it's either file name or summary so should not be limited
        if len(rows) > 0:
            r = 0
            column_formats = []
            for r in range(len(rows[0]) - 1):
                width = max([len(str(row[r])) for row in rows])
                column_format = '{: >%d}' % width
                column_formats.append(column_format)
            row_format = '  '.join(column_formats)
            row_format += ' {}'
            for row in rows:
                ui.log(row_format.format(*row))
