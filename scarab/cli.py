# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
Entry point for CLI utility
"""

from .commands import create_parser
from .context import set_default_config_file

def main():
    """Entry point function for scarab CLI"""
    parser = create_parser()
    args = parser.parse_args()
    if not args.config is None:
        set_default_config_file(args.config)

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
