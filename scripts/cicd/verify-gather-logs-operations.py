#!/usr/bin/python
'''
Validates command to gather logs from a cluster

Developer usage:

   ssh -i log_gathering_key use-tower2.ops.rhcloud.com <clusterName>

clusterName is checked against a list of known/valid cluster names.
'''

# pylint: disable=invalid-name
# pylint: disable=logging-not-lazy
# pylint: disable=bare-except

# The log_gathering_key is kept in the shared-secrets repo. It is generated and
# rotated weekly by the Jenkins job cluster/rotate-log-access-key. The public
# key in .ssh/authorized_keys looks like this:
#
#  command="verify-gather-logs-operations.py" ssh-rsa ThePublicKey logs_access_key_week_22-YMD-H:M:S

import os
import sys
import socket
import logging
import logging.handlers

VALID_CLUSTER_NAMES = [
    'free-int',
    'free-stg',
    'starter-us-east-1',
    'starter-us-east-2',
    'starter-us-west-2'
]

LOG_GATHER_CMD = '/home/opsmedic/aos-cd/git/aos-cd-jobs/tower-scripts/bin/gather-logs.sh'

def runner(program, *args):
    ''' Runs the specified program with args via exec. The function never returns '''

    try:
        os.execlp(program, program, *args)
    except:
        pass
    print "exec failed for command: " + str.join(" ", [program] + list(args))
    sys.exit(11)

logger = logging.getLogger('verify_command_logger')
logger.setLevel(logging.INFO)
logger.addHandler(logging.handlers.SysLogHandler('/dev/log'))

# The requested cluster comes as SSH_ORIGINAL_COMMAND.
# Validate that it's a valid/known cluster name
clustername = os.environ.get("SSH_ORIGINAL_COMMAND", "")
if clustername in VALID_CLUSTER_NAMES:
    logger.info("%s Gathering logs for cluster %s" %
                (os.path.basename(__file__), clustername))
    runner(LOG_GATHER_CMD, clustername)
    # runner never returns

logger.info("%s Log gathering disallowed command: '%s'" %
            (os.path.basename(__file__), clustername))
print "doesn't match an allowed pattern"
print "REJECTED ON HOST: " + socket.gethostname()
print "REJECTED COMMAND: " + clustername
sys.exit(10)
