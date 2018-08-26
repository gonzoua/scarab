# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from commands import create_parser

def main():
    """Main entry point for scarab CLI"""
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
