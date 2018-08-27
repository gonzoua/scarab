# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementation of 'submit' command
"""

from ..context import bugzilla_instance, settings_instance
from ..bugzilla import BugzillaError
from .. import ui
from .base import Base

class Command(Base):
    """Submit new PR"""

    def register(self, subparsers):
        """Register parser for 'submit' command"""
        parser = subparsers.add_parser('submit')
        parser.set_defaults(func=self.run)
        parser.add_argument('-t', '--template', dest='template', \
            help='name of the pre-configured bug template')
        parser.add_argument('-p', '--product', dest='product', \
            help='name of the product')
        parser.add_argument('-c', '--component', dest='component', \
            help='name of the component')
        parser.add_argument('-v', '--version', dest='version', \
            help='version value')
        parser.add_argument('-s', '--summary', dest='summary', \
            required=True, help='summary for the attachment')
        parser.add_argument('-d', '--description', dest='description', help='description text')
        parser.add_argument('-C', '--cc', dest='cc', \
            action='append', help='users to add to CC list (can be specified multiple times)')

    def run(self, args):
        """Implement 'submit' command"""

        template = None
        if args.template:
            template = settings_instance().template(args.template)

        if template:
            product = template.get('product', None)
            component = template.get('component', None)
            version = template.get('version', None)

        # Values specified from command line override
        # values from template
        if args.product:
            product = args.product
        if args.component:
            component = args.component
        if args.version:
            version = args.version

        # product, component and version
        if product is None:
            ui.fatal('product value was not specified')
        if component is None:
            ui.fatal('component value was not specified')
        if version is None:
            ui.fatal('version value was not specified')

        summary = args.summary
        description = args.description
        cc_list = args.cc

        bugzilla = bugzilla_instance()
        try:
            bug = bugzilla.submit(product, component, version, summary, \
                description=description, cc_list=cc_list)
            print(bug)
        except BugzillaError as exc:
            ui.fatal('Bugzilla error: {}'.format(exc.message))
