# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys

def fatal(line):
    sys.stderr.write('FATAL: {}\n'.format(line))
    sys.exit(1)

def log(line):
    sys.stderr.write('{}\n'.format(line))
