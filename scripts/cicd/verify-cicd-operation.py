#!/usr/bin/python
''' string '''

# pylint: disable=invalid-name
# pylint: disable=superfluous-parens
# pylint: disable=logging-not-lazy
# pylint: disable=bare-except
# pylint: disable=star-args

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

program_to_run = "/home/opsmedic/aos-cd/git/aos-cd-jobs/tower-scripts/bin/cicd-control.sh"

valid_operations = ['build-ci-msg',
                    'commit-config-loop',
                    'delete',
                    'disable-config-loop',
                    'disable-statuspage',
                    'disable-zabbix-maint',
                    'enable-config-loop',
                    'enable-statuspage',
                    'enable-zabbix-maint',
                    'generate-byo-inventory',
                    'install',
                    'legacy-upgrade',
                    'perf1',
                    'perf2',
                    'perf3',
                    'pre-check',
                    'run-config-loop',
                    'smoketest',
                    'status',
                    'update-inventory',
                    'update-yum-extra-repos',
                    'upgrade',
                    'upgrade-control-plane',
                    'upgrade-logging',
                    'upgrade-metrics',
                    'upgrade-nodes',
                   ]

def build_arg_list(clusterid, operation, *args):
    ''' build a list of args '''

    arg_list = ['-c', clusterid, '-o', operation]

    for arg in args:
        arg_list += ['-a', arg]

    return arg_list

def runner(program, *args):
    ''' run the script that is intended '''
    try:
        os.execlp(program, program, *args)
    except:
        pass
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
cmd_args = cmd.split()

if len(cmd_args) == 0:
    print("No operation specified")
    sys.exit(11)

operation_from_ssh = cmd_args.pop(0)  # Remove operation string from argument list and store
if operation_from_ssh not in valid_operations:
    logger.info("%s Restricted key '%s' disallowed operation: %s" % (os.path.basename(__file__),
                                                                     cluster_id, operation_from_ssh))
    print("The requested operation isn't in the set of pre-approved operations")
    print("REJECTED ON HOST: " + socket.gethostname())
    sys.exit(10)

# Validate remaining arguments against strict patterns.
# Only matched patters may be passed on to cicd-control. See approved list
# at the top of this file.
# TODO: This needs to be streamlined
operation_args = []
for s in cmd_args:
    if re.match("(^docker_version=[a-zA-Z0-9._-]+$)", s):  # Example docker version: docker-1.12.6-30.git97ba2c0.el7
        operation_args.append(s)
    elif re.match("(^openshift_ansible_build=[a-zA-Z0-9./-]+$)", s):  # Example: 3.6.126.11/1.git.0.bd61c80.el7
        operation_args.append(s)
    else:
        logger.info("%s Restricted key '%s' disallowed argument: %s" % (os.path.basename(__file__), cluster_id, s))
        print("Argument doesn't match an allowed pattern")
        print("REJECTED ON HOST: " + socket.gethostname())
        sys.exit(11)

logger.info("%s Restricted key '%s' running command: %s" % (os.path.basename(__file__), cluster_id, cmd))

args_to_send = build_arg_list(cluster_id, operation_from_ssh, *operation_args)
runner(program_to_run, *args_to_send)
