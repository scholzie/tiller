import logging
from functools import wraps
import subprocess
import os

class TillerException(Exception):
    """Wrapper for Tiller Exceptions"""
    def __init__(self, *args, **kwargs):
        super(TillerException, self).__init__(self, *args, **kwargs)


def logged(level=logging.DEBUG, name=None, msg=None):
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


def change_log_level(level, logger=None):
    '''
    If the current logging level is higher than the specified level, 
    set the indicated logger's level to the indicated logging.LEVEL for the
    duration of that function.
    '''
    def decorate(func):
        # logname = logger if logger else func.__module__
        log = logging.getLogger()
        print "new level is " + level
        @wraps(func)
        def wrapper(*args, **kwargs):
            oldLogLevel = log.level
            if oldLogLevel > level:
                log.setLevel(level)
            retval = func(*args, **kwargs)
            log.setLevel(oldLogLevel)
            return retval
        return wrapper
    return decorate


# def upgrade_logging(func, level, logger=None):

#     def wrapper(*args, **kwargs):
#         logname = logger if logger else func.__module__
#         print logname
#         log = logging.getLogger()
#         print log
#         oldLogLevel = log.level
#         print oldLogLevel
#         if oldLogLevel > level:
#             print "Changing log level"
#             log.setLevel(level)
#         print "Returning %s"  % func
#         return func(*args, **kwargs)
        
#         print "resetting log level to %s" % oldLogLevel
#         log.setLevel(oldLogLevel)

#     print "returning wrapper"
#     return wrapper


def run(cmd, args=None, cwd=None, log_only=False):
    args = args if args else []
    cwd = cwd if cwd else os.path.curdir
    try:
        logging.debug(cmd+args)
        p = subprocess.Popen(cmd + args,
                             env=os.environ,
                             cwd=cwd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, ''):
            if log_only:
                logging.info(line.rstrip('\n'))
            else:
                print(line.rstrip('\n'))
        p.stdout.close()
        p.wait()
        logging.debug("`{}` exited with code {}".format(' '.join(cmd+args), p.returncode))
        return p.returncode
    except Exception as e:
        logging.error(e)
        raise
    else:
        return False
    