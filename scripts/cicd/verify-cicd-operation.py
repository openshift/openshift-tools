#!/usr/bin/python
''' verify the cicd operation command coming in from Jenkins via SSH '''

# pylint: disable=invalid-name
# pylint: disable=bare-except
# pylint: disable=too-many-instance-attributes

#Jenkins:
#ssh use-tower1.ops.rhcloud.com -c clustername -o <operation> -e [approved_arg1] -e [approved_arg2] ...

# Current approved arguments:
#   "docker-version=<rpmname-version-release>"
#       This argument specifies a docker RPM NVR that should be used for openshift-ansible upgrade operations.
#       An example "NVR: docker-1.12.6-30.git97ba2c0.el7"
#
# Pull requests which add new arguments must be approved by the security team.
#
#Associate the cluster to operate on with an ssh key in .ssh/authorized_keys
# command=verify-cicd-operation.py -e <environment> <really long key right here>

import argparse
import logging
import logging.handlers
import os
import re
import sys
import yaml

PROGRAM_TO_RUN = "/home/opsmedic/aos-cd/git/aos-cd-jobs/tower-scripts/bin/cicd-control.sh"

VALID_OPERATIONS = ['build-ci-msg',
                    'commit-config-loop',
                    'delete',
                    'delete-yum-repos',
                    'disable-config-loop',
                    'disable-statuspage',
                    'disable-zabbix-maint',
                    'enable-config-loop',
                    'enable-statuspage',
                    'enable-zabbix-maint',
                    'generate-byo-inventory',
                    'install',
                    'legacy-upgrade',
                    'online-deployer',
                    'perf1',
                    'perf2',
                    'perf3',
                    'pre-check',
                    'run-config-loop',
                    'schedule-all-nodes',
                    'set-yum-repos',
                    'smoketest',
                    'status',
                    'storage-migration',
                    'unschedule-extra-nodes',
                    'update-inventory',
                    'update-jenkins-imagestream',
                    'update-yum-extra-repos',
                    'upgrade',
                    'upgrade-control-plane',
                    'upgrade-logging',
                    'upgrade-metrics',
                    'upgrade-nodes',
                   ]

# this is a list of extra arguments that are valid and their corresponding regular expression.
VALID_EXTRA_ARGUMENTS = {'cicd_docker_version' : '^$|^[a-zA-Z0-9._-]+$',
                         'cicd_openshift_ansible_build' : '^$|^[a-zA-Z0-9./-]+$',
                         'cicd_openshift_version' : '^$|^[a-zA-Z0-9./-]+$',
                         'cicd_yum_main_url' : '^$|^[a-zA-Z0-9./:_-]+$',
                         'cicd_yum_openshift_ansible_url' : '^$|^[a-zA-Z0-9./:_-]+$',
                        }

class VerifyCICDOperation(object):
    """ Verify CICD SSH Command """

    def __init__(self):
        """ This is the init function """

        self.clustername = None
        self.operation = None
        self.environment = None
        self.deployment_type = None
        self.ssh_original_args = None
        self.extra_arguments = []
        self.cicd_control_args = None

        # set up the logger
        self.logger = logging.getLogger('verify_cicid_command_logger')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.handlers.SysLogHandler('/dev/log'))

    def run(self):
        """ Main function to run the script """

        self.logger.info("{}: Args: {}, SSH_ORIGINAL_COMMAND: '{}'".format(os.path.basename(__file__), sys.argv,
                                                                           os.environ.get("SSH_ORIGINAL_COMMAND", "")))

        self.cli_parse_args()
        self.ssh_original_parse_args()

        self.verify_cluster()
        self.verify_operation()
        if self.ssh_original_args.extra_args:
            self.verify_extra_arguments()

        self.build_arg_list()
        VerifyCICDOperation.runner(*self.cicd_control_args)

    def cli_parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Verify CICD Arg Parsing')

        parser.add_argument('-e', '--environment', help='Environment', default=None, required=True)

        cli_args = parser.parse_args()
        self.environment = cli_args.environment

    def ssh_original_parse_args(self):
        """ parse the args from the SSH_ORIGINAL_COMMAND env var """

        parser = argparse.ArgumentParser(description='Verify CICD SSH_ORIGINAL_COMMAND Arg Parsing',
                                         usage="ENV Var: 'SSH_ORIGINAL_COMMAND' needs to be set correctly")

        parser.add_argument('-c', '--cluster', help='Ops Cluster name', default=None, required=True)

        parser.add_argument('-o', '--operation', help='Operation to perform', choices=VALID_OPERATIONS,
                            default=None, required=True)

        parser.add_argument('-d', '--deployment', help='Deployment Type', choices=['dedicated', 'online', 'pro'],
                            default='online', required=False)

        parser.add_argument('-e', '--extra-args', help='Extra argmuments to pass on', action='append',
                            default=None, required=False)

        # We want to parse the SSH_ORIGINAL_COMMAND ENV var which comes through SSH
        ssh_cmd = os.environ.get("SSH_ORIGINAL_COMMAND", "")
        ssh_cmd_args = ssh_cmd.split()

        if not ssh_cmd_args:
            self.exit_with_msg("Environment variable 'SSH_ORIGINAL_COMMAND' is empty. Exiting...")

        self.ssh_original_args = parser.parse_args(ssh_cmd_args)

        self.clustername = self.ssh_original_args.cluster
        self.operation = self.ssh_original_args.operation
        self.deployment_type = self.ssh_original_args.deployment

    def exit_with_msg(self, message, exit_code=13):
        ''' Let's do all of our exiting here.  With logging '''

        self.logger.info("{}: Exiting on Error: {}".format(os.path.basename(__file__), message))
        print message
        sys.exit(exit_code)

    @staticmethod
    def get_clusters():
        ''' get the clusters from the inventory file '''

        with open('/etc/ansible/multi_inventory.yaml') as f:
            inventory_data = yaml.safe_load(f)

        clusters = {}
        for account, account_vars in inventory_data['accounts'].iteritems():

            if 'cluster_vars' not in account_vars:
                continue

            for cluster, cluster_vars in account_vars["cluster_vars"]["clusters"].iteritems():
                clusters[cluster] = {'environment': cluster_vars["oo_environment"],
                                     'account': account
                                    }

        # Hard coding the "test-key cluster, which is int env"
        clusters['test-key'] = {'environment': 'int',
                                'account': 'test'
                               }
        return clusters

    def verify_cluster(self):
        ''' verify the cluster is valid '''

        # Sanity check the cluster_id
        if not re.match("(^[a-zA-Z0-9][a-zA-Z0-9._-]+$)", self.clustername):
            print "Clustername did not match the approved Regular Expression."
            sys.exit(13)

        clusters = VerifyCICDOperation.get_clusters()

        if self.clustername not in clusters:
            self.exit_with_msg("Clustername was not found in the list of known clusters. Exiting...")

        if self.environment != clusters[self.clustername]['environment']:
            self.exit_with_msg("The environment passed does NOT match the cluster's env. Exiting...")

    def verify_operation(self):
        ''' verify the operation is valid '''

        # Sanity check the operation
        if not re.match("(^[a-zA-Z0-9][a-zA-Z0-9._-]+$)", self.operation):
            self.exit_with_msg("operation did not match the approved Regular Expression.")

    def verify_extra_arguments(self):
        ''' verify the extra arguments are valid '''

        for arg in self.ssh_original_args.extra_args:
            split_arg = arg.split("=")

            if len(split_arg) != 2:
                self.exit_with_msg("Extra argmument: '{}' did not match the the approved var structure".format(arg))

            if split_arg[0] not in VALID_EXTRA_ARGUMENTS.keys():
                self.exit_with_msg("Extra argmument: '{}' is not an approved extra argument".format(arg))

            if not re.match(VALID_EXTRA_ARGUMENTS[split_arg[0]], split_arg[1]):
                self.exit_with_msg("Extra argmument: '{}' does not match approved regular expression: "
                                   "'{}'".format(arg, VALID_EXTRA_ARGUMENTS[split_arg[0]]))

            self.extra_arguments.append(arg)

    def build_arg_list(self):
        ''' build a list of args '''

        self.cicd_control_args = ['-c', self.clustername, '-o', self.operation,
                                  '-d', self.deployment_type]

        for arg in self.extra_arguments:
            self.cicd_control_args += ['-e', arg]

    @staticmethod
    def runner(*args):
        ''' run the script that is intended '''

        try:
            os.execlp(PROGRAM_TO_RUN, PROGRAM_TO_RUN, *args)
        except:
            pass
        sys.exit(11)
        # runner (exec) never returns

if __name__ == "__main__":
    VCO = VerifyCICDOperation()
    VCO.run()
