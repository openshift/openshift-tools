#!/usr/bin/python

'''
Validates command to gather logs from a cluster

Developer usage:

   ssh -i log_gathering_key use-tower2.ops.rhcloud.com -- -c <clusterName> -u <kerberosID>

clusterName is checked against a list of known/valid cluster names.

kerberosID is the Kerberos ID of the developer requesting logs, for tracking purposes
'''

# pylint: disable=invalid-name
# pylint: disable=logging-not-lazy
# pylint: disable=broad-except

# The log_gathering_key is kept in the shared-secrets repo. It is generated and
# rotated weekly by the Jenkins job cluster/rotate-log-access-key. The public
# key in .ssh/authorized_keys looks like this:
#
#  command="verify-gather-logs-operations.py" ssh-rsa ThePublicKey logs_access_key_week_22-YMD-H:M:S

import argparse
import os
import re
import sys
import socket
import logging
import logging.handlers

# The list of valid cluster names to request logs from
VALID_CLUSTER_NAMES = [
    'free-int',
    'free-stg',
    'starter-us-east-1',
    'starter-us-east-2',
    'starter-us-west-2'
]

# The command that is invoked to perform the actual log collection.  This
# command should expect one argument, the cluster name on which to operate, and
# produce the logs as a tarball in stdout, which gets passed directly as the
# output of this script.
LOG_GATHER_CMD = '/home/opsmedic/aos-cd/git/aos-cd-jobs/tower-scripts/bin/gather-logs.sh'

HOSTNAME = socket.gethostname()

logger = logging.getLogger('verify_command_logger')
logger.setLevel(logging.INFO)
logger.addHandler(logging.handlers.SysLogHandler('/dev/log'))

def valid_krbid(username):
    '''Sanity check that the username looks like valid according to the description
    of valid usernames from useradd(8)
    '''
    if re.match(r'^[a-z_][a-z0-9_-]*[$]?$', username) and len(username) <= 32:
        return username
    else:
        raise argparse.ArgumentTypeError("Kerberos ID was not provided in acceptable format")

def gather_logs(command):
    '''Main function that parses arguments and execs the cluster log
    gathering command.

    This function never returns (it can raise exceptions though)
    '''

    invocation = "ssh -i gather_logs_key %s --" % HOSTNAME
    parser = argparse.ArgumentParser(prog=invocation)
    parser.add_argument('-u', dest='user', help="Your kerberos ID",
                        required=True, type=valid_krbid)
    parser.add_argument('-c', dest='cluster', help="Cluster name",
                        required=True, choices=VALID_CLUSTER_NAMES)

    args = parser.parse_args(command.split())
    os.execlp(LOG_GATHER_CMD, LOG_GATHER_CMD, args.cluster)

if __name__ == '__main__':
    cmd = os.environ.get("SSH_ORIGINAL_COMMAND", "")
    logger.info("%s invoked with arguments: %s" %
                ((os.path.basename(__file__)), cmd))
    try:
        gather_logs(cmd)
    except Exception as e:
        logger.info("%s Cluster log gathering failed command '%s': %s" %
                    ((os.path.basename(__file__)), cmd, e))
    # The gather_logs() function should never return, as it exec's the program
    # to produce the logs. If we're here, something went wrong:
    sys.exit(10)
