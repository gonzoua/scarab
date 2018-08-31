# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
Module handles all the interactoins with user
"""
import sys, tempfile, os
from subprocess import call

MESSAGE = '''
# SCARAB: Please enter the comment. Lines starting with '# SCARAB:'
# SCARAB: will be ignored
'''

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

def edit_message(initial_message = None):
    """
    Invoke editor to let user provide multi-line input. All lines starting
    with '# SCARAB:' are considered internal comments and ignored. Leading
    and trailing spaces are removed from final comment
    """
    editor = os.environ.get('SCARAB_EDITOR', None)
    if editor is None:
        editor = os.environ.get('EDITOR', 'vi')

    tf = tempfile.NamedTemporaryFile(suffix=".tmp", mode="w+", delete=False)
    if not initial_message is None:
        tf.write(initial_message)
    tf.write(MESSAGE)
    tf.flush()
    name = tf.name
    tf.close()

    call([editor, name])

    with open(name, 'r') as tf:
        message = tf.read()

    os.unlink(name)

    lines = message.split('\n')
    lines = [l for l in lines if not l.startswith('# SCARAB:')]
    message = '\n'.join(lines).strip()

    return message
