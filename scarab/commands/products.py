# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
Implementation of 'products' command
"""

from ..context import bugzilla_instance
from ..bugzilla import BugzillaError
from .. import ui
from .base import Base

class Command(Base):
    """List products information"""

    def register(self, subparsers):
        """Register parser for 'products' command"""
        parser = subparsers.add_parser('products')
        parser.set_defaults(func=self.run)

    def run(self, args):
        """Implement 'products' command"""

        bugzilla = bugzilla_instance()
        try:
            products = bugzilla.products()
        except BugzillaError as exc:
            ui.fatal('Bugzilla error: {}'.format(exc.message))

        for product in products:
            ui.output("Product '{}':".format(product.name))
            ui.output('  components:')
            for component in product.components:
                ui.output('    {}'.format(component.name))
            ui.output('  versions:')
            for version in product.versions:
                ui.output('    {}'.format(version.name))
