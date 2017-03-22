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

def runner(program, *args):
    ''' string '''

    try:
        os.execlp(program, program, *args)
    except:
        pass
    print("exec failed for command: " + str.join(" ", [program]+list(args)))
    sys.exit(11)
    # runner never returns

logger = logging.getLogger('verify_command_logger')
logger.setLevel(logging.INFO)
logger.addHandler(logging.handlers.SysLogHandler('/dev/log'))

keyname = sys.argv[1] if len(sys.argv) >= 2 else "<none specified>"
cmd = os.environ.get("SSH_ORIGINAL_COMMAND", "")

# Allow alphanumerics, whitespace, -, =. Permits command lines like "install --openshift-ansible=3.6.30"
match = re.match("^[\\w\\s\\-\\=.]+$", cmd)

if match:
    logger.info("%s Restricted key '%s' running command: %s" % (os.path.basename(__file__), keyname, cmd))
    runner("/home/opsmedic/aos-cd/git/aos-cd-jobs/bin/cicd-control.sh", *[keyname]+match.group().split())

logger.info("%s Restricted key '%s' disallowed command: %s" % (os.path.basename(__file__), keyname, cmd))
print("doesn't match an allowed pattern")
print("REJECTED ON HOST: " + socket.gethostname())
print("REJECTED COMMAND: " + cmd)
sys.exit(10)
