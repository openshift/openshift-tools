# vim: expandtab:tabstop=4:shiftwidth=4

''' The purpose of this module is to give a decorator and anonymous block
    statement that can be used to timeout a function or block of code if
    it runs for too long.

    Example Usage:
        from openshift_tools.timeout import timeout, timed

        @timed(20)
        def some_function():
            # do something that should always finish within 20 seconds

        def some_function():
            with timeout(seconds=20):
                # do something that should always finish within 20 seconds
'''

import signal
from functools import wraps

class TimeoutException(Exception):
    ''' For raising timeouts '''
    pass

def timed(seconds):
    ''' Use as a decorator to timeout a function after so many seconds '''

    def outer(decorated_function):
        ''' Outer function of the decorator '''

        @wraps(decorated_function)
        def wrapper(*args, **kwargs):
            ''' Wraps the decorated function, where the magic happens '''

            with timeout(seconds=seconds):
                result = decorated_function(*args, **kwargs)

            return result
        return wrapper
    return outer

# Reason: disable pylint invalid-name
#         pylint does not like the name 'timeout'
# Status: permanently disabled
# pylint: disable=invalid-name
class timeout(object):
    ''' anonymous block for setting arbritrary timeouts '''

    # Reason: disable pylint too-few-public-methods
    # Status: permanently disabled
    # pylint: disable=too-few-public-methods
    def __init__(self, seconds, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
        self.old_handler = None

    def handle_timeout(self, signum, frame):
        ''' called in the event of a timeout. just raise an exception '''

        del signum #make pylint happy
        del frame  #make pylint happy
        raise TimeoutException(self.error_message)

    def __enter__(self):
        self.old_handler = signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    # Reason: disable pylint redefined-builtin
    # Status: permanently disabled
    # pylint: disable=redefined-builtin
    def __exit__(self, type, value, traceback):
        # Reset the alarm
        signal.alarm(0)

        # make sure the original handler is now back in place
        signal.signal(signal.SIGALRM, self.old_handler)
