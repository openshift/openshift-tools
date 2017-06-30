#!/usr/bin/python
''' string '''

# pylint: disable=invalid-name
# pylint: disable=superfluous-parens
# pylint: disable=logging-not-lazy
# pylint: disable=bare-except

#Jenkins:
#ssh use-tower1.ops.rhcloud.com <operation> [approved_arg1] [approved_arg2] ...
# Current approved arguments:
#   "docker-version=<rpmname-version-release>"
#       This argument specifies a docker RPM NVR that should be used for openshift-ansible upgrade operations.
#       An example "NVR: docker-1.12.6-30.git97ba2c0.el7"
#
# Pull requests which add new arguments must be approved by the security team.
#
#Associate the cluster to operate on with an ssh key in .ssh/authorized_keys
# command=verify-cicd-operation.py <clusterid> <really long key right here>

import re
import os
import sys
import socket
import logging
import logging.handlers

def runner(program, *args):
    try:
        os.execlp(program, program, *args)
    except:
        pass
    print("exec failed for command: " + str.join(" ", [program] + list(args)))
    sys.exit(11)
    # runner never returns

logger = logging.getLogger('verify_command_logger')
logger.setLevel(logging.INFO)
logger.addHandler(logging.handlers.SysLogHandler('/dev/log'))

# The cluster_id argument is provided by the authorized_keys command entry for the ssh user's private key.
# In other words, the ssh user cannot specify the cluster_id directly (they must have the correct private key
# AND the key must be setup in the authorized_keys file appropriately).
if len(sys.argv) != 2:
    print("No cluster identifier specified")
    sys.exit(12)

cluster_id = sys.argv[1]

# Sanity check the cluster_id from authorized_keys
if not re.match("(^[a-zA-Z0-9][a-zA-Z0-9._-]+$)", cluster_id):
    print("Invalid cluster identifier specified")
    sys.exit(13)

cmd = os.environ.get("SSH_ORIGINAL_COMMAND", "")
args = cmd.split()

if len(args) == 0:
    print("No operation specified")
    sys.exit(11)

op = args.pop(0)  # Remove operation string from argument list and store

match = re.match(r"(?P<operation>install|delete|upgrade|status|logs|perf1|perf2|perf3|build-ci-msg|smoketest)", op)

if not match:
    logger.info("%s Restricted key '%s' disallowed operation: %s" % (os.path.basename(__file__), cluster_id, op))
    print("Operation doesn't match an allowed pattern ")
    print("REJECTED ON HOST: " + socket.gethostname())
    sys.exit(10)

# Validate remaining arguments against strict patterns.
# Only matched patters may be passed on to cicd-control. See approved list
# at the top of this file.
operation_args = []
for s in args:
    if re.match("(^docker-version=[a-zA-Z0-9._-]+$)", s):  # Example docker version: docker-1.12.6-30.git97ba2c0.el7
        operation_args.append("--" + s)
    else:
        logger.info("%s Restricted key '%s' disallowed argument: %s" % (os.path.basename(__file__), cluster_id, s))
        print("Argument doesn't match an allowed pattern")
        print("REJECTED ON HOST: " + socket.gethostname())
        sys.exit(11)

logger.info("%s Restricted key '%s' running command: %s" % (os.path.basename(__file__), cluster_id, cmd))

runner("/home/opsmedic/aos-cd/git/aos-cd-jobs/tower-scripts/bin/cicd-control.sh",
       cluster_id,
       match.group("operation"),
       *operation_args)

