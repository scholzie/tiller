import logging
from functools import wraps

class TillerException(Exception):
    """Wrapper for Tiller Exceptions"""
    def __init__(self, *args, **kwargs):
        super(TillerException, self).__init__(self, *args, **kwargs)


def logged(level, name=None, msg=None):
    '''
    Add logging to a function. level is logging.LEVEL,
    name is the logger name, and msg is the log message.
    If name and msg are not defined, they default to the
    function's module and name
    '''
    def decorate(func):
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        if msg:
            logmsg = '{}(): {}'.format(func.__name__, msg)
        else:
            logmsg = func.__name__ + "()"

        @wraps(func)
        def wrapper(*args, **kwargs):
            log.log(level, logmsg)
            return func(*args, **kwargs)
        return wrapper
    return decorate
