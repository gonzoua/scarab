# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementation of 'submit' command
"""

import argparse

from ..context import bugzilla_instance, settings_instance
from ..settings import Settings
from ..bugzilla import BugzillaError
from .. import ui
from .base import Base

class Command(Base):
    """Submit new PR"""

    def register(self, subparsers):
        """Register parser for 'submit' command"""
        parser = subparsers.add_parser('submit')
        parser.set_defaults(func=self.run)
        parser.add_argument('-b', '--batch', action='store_true', \
            help='batch mode, only print newly created bug\'s id')
        parser.add_argument('-t', '--template', dest='templates', \
            action='append', help='name of the pre-configured bug template')
        parser.add_argument('-p', '--product', dest='product', \
            help='name of the product')
        parser.add_argument('-m', '--component', dest='component', \
            help='name of the component')
        parser.add_argument('-v', '--version', dest='version', \
            help='version value')
        comment_group = parser.add_mutually_exclusive_group()
        comment_group.add_argument('-c', '--comment', dest='comment', \
            help='comment describing the bug')
        comment_group.add_argument('-F', '--comment-file', dest='comment_file', \
            type=argparse.FileType('r'), help='file with comment text')
        parser.add_argument('-s', '--summary', dest='summary', \
            required=True, help='summary for the bug')
        parser.add_argument('-C', '--cc', dest='cc', \
            action='append', help='users to add to CC list (can be specified multiple times)')
        parser.add_argument('-P', '--platform', dest='platform', help='platform')
        parser.add_argument('-S', '--severity', dest='severity', help='severity')

    def run(self, args):
        """Implement 'submit' command"""

        template = None
        try:
            if args.templates:
                template = settings_instance().combine_templates(args.templates)
        except Settings.TemplateNotFound as ex:
            ui.fatal("Template '{}' is not defined".format(ex.template_name))

        product = None
        component = None
        version = None
        severity = None
        platform = None

        if template:
            product = template.get('product', None)
            component = template.get('component', None)
            version = template.get('version', None)
            severity = template.get('severity', None)
            platform = template.get('platform', None)

        # Values specified from command line override
        # values from template
        if args.product:
            product = args.product
        if args.component:
            component = args.component
        if args.version:
            version = args.version
        if args.severity:
            severity = args.severity
        if args.platform:
            platform = args.platform

        # product, component and version
        if product is None:
            ui.fatal('product value was not specified')
        if component is None:
            ui.fatal('component value was not specified')
        if version is None:
            ui.fatal('version value was not specified')

        summary = args.summary
        cc_list = args.cc

        comment = args.comment
        if comment is None:
            if args.comment_file:
                comment = args.comment_file.read()
        if comment is None:
            if args.batch:
                comment = ''
            else:
                comment = ui.edit_message()

        bugzilla = bugzilla_instance()
        try:
            bug = bugzilla.submit(product, component, version, summary, \
                description=comment, cc_list=cc_list, severity=severity, \
                platform=platform)
        except BugzillaError as exc:
            ui.fatal('Bugzilla error: {}'.format(exc.message))

        if args.batch:
            ui.output('{}'.format(bug))
        else:
            ui.output('New bug {} has been submitted'.format(bug))
            ui.output('Bug URL: {}'.format(bugzilla.bug_url(bug)))
