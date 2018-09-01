# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementatoin of the 'files' command
"""

from datetime import datetime, timezone

from ..bugzilla import BugzillaError
from ..context import bugzilla_instance
from .. import ui
from .base import Base

class Command(Base):
    """Show info for specific PR"""

    def register(self, subparsers):
        parser = subparsers.add_parser('info')
        parser.set_defaults(func=self.run)
        parser.add_argument('bug_id', type=int, help='bug ID')

    def run(self, args):
        bugzilla = bugzilla_instance()
        try:
            bug = bugzilla.bug(args.bug_id)
            bug_description = bugzilla.bug_description(args.bug_id)
        except BugzillaError as exc:
            ui.fatal('Bugzilla error: {}'.format(exc.message))

        row_format = '{: >16}: {}'
        ui.output(row_format.format('Bug ID', bug.object_id))
        ui.output(row_format.format('Summary', bug.summary))
        ui.output(row_format.format('Product', bug.product))
        ui.output(row_format.format('Version', bug.version))
        ui.output(row_format.format('OS', bug.os))
        ui.output(row_format.format('Status', bug.status))
        ui.output(row_format.format('Resolution', bug.resolution))
        ui.output(row_format.format('Severity', bug.severity))
        ui.output(row_format.format('Priority', bug.priority))
        ui.output(row_format.format('Component', bug.component))
        ui.output(row_format.format('Assignee', bug.assigned_to))
        ui.output(row_format.format('Reporter', bug.creator))
        ui.output('')
        ui.output(bug_description)
