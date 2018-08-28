# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
Entry point for CLI utility
"""

from .commands import create_parser

def main():
    """Entry point function for scarab CLI"""
    parser = create_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
