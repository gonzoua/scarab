# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementation of attachment flags-related commands
"""

import os

from .base import Base
from ..context import bugzilla_instance
from ..bugzilla import BugzillaError
from .. import ui

class Command(Base):
    """Attachment flags operations: add/remove/set"""

    def register(self, subparsers):
        """Register parser for attachment flags-related commands"""
        parser_ls = subparsers.add_parser('aflags')
        parser_ls.set_defaults(func=self.run_ls)
        parser_ls.add_argument('attachment_id', type=int, help='attachment ID')

        parser_add = subparsers.add_parser('addaflag')
        parser_add.set_defaults(func=self.run_add)
        parser_add.add_argument('attachment_id', type=int, help='attachment ID')
        parser_add.add_argument('name', type=str, help='flag name')
        parser_add.add_argument('requestee', type=str, nargs='?', help='requestee')

        parser_rm = subparsers.add_parser('rmaflags')
        parser_rm.set_defaults(func=self.run_rm)
        parser_rm.add_argument('attachment_id', type=int, help='attachment ID')
        parser_rm.add_argument('name', type=str, nargs='+', help='flag name')

        parser_set = subparsers.add_parser('setaflag')
        parser_set.set_defaults(func=self.run_set)
        parser_set.add_argument('attachment_id', type=int, help='attachment ID')
        parser_set.add_argument('name', type=str, help='flag name')
        parser_set.add_argument('status', type=str, choices=['+', '-'], help='flag status')

    def run_ls(self, args):
        """Implementation of the 'aflags' command"""
        bugzilla = bugzilla_instance()
        try:
            attachemnt = bugzilla.attachment(args.attachment_id)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))
        if attachemnt is None:
            ui.fatal('No such attachment # {}'.format(args.attachment_id))

        rows = []
        for f in attachemnt.flags:
            row = []
            row.append(str(f.object_id))
            row.append(f.name)
            row.append(f.status)
            row.append(f.requestee)
            rows.append(row)

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

    def run_add(self, args):
        """Implementation of the 'addaflag' command"""
        bugzilla = bugzilla_instance()
        try:
            bugzilla.add_aflag(args.attachment_id, args.name, args.requestee)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))

    def run_rm(self, args):
        """Implementation of the 'rmaflags' command"""
        bugzilla = bugzilla_instance()
        try:
            bugzilla.rm_aflags(args.attachment_id, args.name)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))

    def run_set(self, args):
        """Implementation of the 'setaflag' command"""
        bugzilla = bugzilla_instance()
        try:
            bugzilla.update_aflag(args.attachment_id, args.name, args.status)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))
