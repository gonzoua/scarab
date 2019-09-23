# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementation of flags command
"""

import os

from .base import Base
from ..context import bugzilla_instance
from ..bugzilla import BugzillaError
from .. import ui

class Command(Base):
    """Flags operations: add/remove/set"""

    def register(self, subparsers):
        """Register parser for flags-related commands"""
        parser_ls = subparsers.add_parser('flags')
        parser_ls.set_defaults(func=self.run_ls)
        parser_ls.add_argument('bug_id', type=int, help='bug ID')

        parser_add = subparsers.add_parser('addflag')
        parser_add.set_defaults(func=self.run_add)
        parser_add.add_argument('bug_id', type=int, help='bug ID')
        parser_add.add_argument('name', type=str, help='flag name')
        parser_add.add_argument('requestee', type=str, nargs='?', help='requestee')

        parser_rm = subparsers.add_parser('rmflags')
        parser_rm.set_defaults(func=self.run_rm)
        parser_rm.add_argument('bug_id', type=int, help='bug ID')
        parser_rm.add_argument('name', type=str, nargs='+', help='flag name')

        parser_set = subparsers.add_parser('setflag')
        parser_set.set_defaults(func=self.run_set)
        parser_set.add_argument('bug_id', type=int, help='bug ID')
        parser_set.add_argument('name', type=str, help='flag name')
        parser_set.add_argument('status', type=str, choices=['+', '-'], help='flag status')

    def run_ls(self, args):
        """Implementation of the 'flags' command"""
        bugzilla = bugzilla_instance()
        try:
            bug = bugzilla.bug(args.bug_id)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))

        rows = []
        for f in bug.flags:
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
        """Implementation of the 'addflag' command"""
        bugzilla = bugzilla_instance()
        try:
            bugzilla.add_flag(args.bug_id, args.name, args.requestee)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))

    def run_rm(self, args):
        """Implementation of the 'rmflags' command"""
        bugzilla = bugzilla_instance()
        try:
            bugzilla.rm_flags(args.bug_id, args.name)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))

    def run_set(self, args):
        """Implementation of the 'setflag' command"""
        bugzilla = bugzilla_instance()
        try:
            bugzilla.update_flag(args.bug_id, args.name, args.status)
        except BugzillaError as ex:
            ui.fatal('Bugzilla error: {}'.format(ex.message))
