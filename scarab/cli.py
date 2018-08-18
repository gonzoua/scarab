# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from commands import create_parser
from settings import Settings

def main():
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
