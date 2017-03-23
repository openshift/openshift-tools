#!/usr/bin/python
''' string '''

# pylint: disable=invalid-name
# pylint: disable=superfluous-parens
# pylint: disable=logging-not-lazy
# pylint: disable=bare-except

#Jenkins:
#ssh use-tower1.ops.rhcloud.com <operation>
#
#in ssh/.authorized_keys
# command=verify-cicd-operation.py <clusterid> <really long key right here>

import re
import os
import sys
import socket
import logging
import logging.handlers

OPTION = r'--openshift-ansible=\d+\.\d+'
ALLOWED_COMMANDS = (
    ['install'],
    ['install', OPTION],
    ['update'],
    ['update', OPTION],
    ['delete'],
    ['delete', OPTION],
)

def runner(program, *args):
    ''' string '''

    try:
        os.execlp(program, program, *args)
    except:
        pass
    print("exec failed for command: " + str.join(" ", [program] + list(args)))
    sys.exit(11)
    # runner never returns

def verify(allowed_args, args):
    """ Check if `args` is valid, according to `allowed_args`. """
    for allowed in allowed_args:
        if len(allowed) != len(args):
            continue
        if all(re.match(pat + '$', arg) for (pat, arg) in zip(allowed, args)):
            return True
    return False

if __name__ == '__main__':
    """ Module entrypoint when executed directly. """
    logger = logging.getLogger('verify_command_logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.handlers.SysLogHandler('/dev/log'))

    keyname = sys.argv[1] if len(sys.argv) >= 2 else "<none specified>"
    cmd = os.environ.get("SSH_ORIGINAL_COMMAND", "").split()
    if verify(ALLOWED_COMMANDS, cmd):
        logger.info("%s Restricted key '%s' running command: %s" % (os.path.basename(__file__), keyname, cmd))
        runner("/home/opsmedic/aos-cd/git/aos-cd-jobs/bin/cicd-control.sh", keyname, *cmd)

    logger.info("%s Restricted key '%s' disallowed command: %s" % (os.path.basename(__file__), keyname, cmd))
    print("doesn't match an allowed pattern")
    print("REJECTED ON HOST: " + socket.gethostname())
    print("REJECTED COMMAND: %s" % (cmd,))
    sys.exit(10)
