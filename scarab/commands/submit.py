# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementation of 'submit' command
"""

from ..context import bugzilla_instance
from ..bugzilla import BugzillaError
from .. import ui
from .base import Base

class Command(Base):
    """Submit new PR"""

    def register(self, subparsers):
        """Register parser for 'submit' command"""
        parser = subparsers.add_parser('submit')
        parser.set_defaults(func=self.run)
        parser.add_argument('-p', '--product', dest='product', \
            required=True, help='name of the product')
        parser.add_argument('-c', '--component', dest='component', \
            required=True, help='name of the component')
        parser.add_argument('-v', '--version', dest='version', \
            required=True, help='version value')
        parser.add_argument('-s', '--summary', dest='summary', \
            required=True, help='summary for the attachment')
        parser.add_argument('-d', '--description', dest='description', help='description text')
        parser.add_argument('-C', '--cc', dest='cc', \
            action='append', help='users to add to CC list (can be specified multiple times)')


    def products(self, args):
        """Implement 'submit' command"""

        bugzilla = bugzilla_instance()
        try:
            products = bugzilla.enterable_products()
        except BugzillaError as exc:
            ui.fatal('Bugzilla error: {}'.format(exc.message))

        for product in products:
            print('{}:'.format(product.name))
            print('  components:')
            for component in product.components:
                print('    {}'.format(component.name))
            print('  versions:')
            for version in product.versions:
                print('    {}'.format(version.name))

    def run(self, args):
        """Implement 'submit' command"""

        product = args.product
        component = args.component
        version = args.version
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
