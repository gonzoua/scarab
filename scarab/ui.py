# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
Module handles all the interactoins with user
"""
import sys

def fatal(line):
    """
    Handle fatal error: log message and abort execution
    """
    sys.stderr.write('{}\n'.format(line))
    sys.exit(1)

def log(line):
    """Log debug/error message"""
    sys.stderr.write('{}\n'.format(line))

def output(line):
    """Output normal message"""
    sys.stdout.write('{}\n'.format(line))
