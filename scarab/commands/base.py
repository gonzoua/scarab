class Base(object):
    """A base command."""
 
    def __init__(self):
        pass

    def register(cls, subparsers):
        raise NotImplementedError('You must implement the register() method yourself!')
        
 
    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')
