# vim: expandtab:tabstop=4:shiftwidth=4

''' The purpose of this module is to give a decorator that can be used to
    timeout a function if it runs for too long.

    Example Usage:
        from openshift_tools.timeout import timeout

        @timeout(20)
        def some_function():
            # do something that should always finish within 20 seconds
'''

import signal
from functools import wraps

class TimeoutException(Exception):
    ''' Class to hold timeout exceptions '''
    pass


def handler(signum, frame):
    ''' Handles the alarm signal '''
    del signum # To make pylint happy
    del frame  # To make pylint happy
    raise TimeoutException("Operation Timed Out")

def timeout(seconds):
    ''' Use as a decorator to timeout a function after so many seconds
    '''
    def outer(decorated_function):
        ''' Outer function of the decorator
        '''
        @wraps(decorated_function)
        def wrapper(*args, **kwargs):
            ''' Wraps the decorated function, where the magic happens
            '''
            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                result = decorated_function(*args, **kwargs)
            finally:
                # Reset the alarm
                signal.alarm(0)

                # make sure the original handler is now back in place
                signal.signal(signal.SIGALRM, old_handler)
            return result
        return wrapper
    return outer
