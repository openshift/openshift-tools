#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
    Tool to process and take action on incoming zabbix triggers.
'''
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name
# pylint: disable=line-too-long

import argparse
import ConfigParser
import logging
import os
import re
import shlex
import subprocess
import sys

class RemoteHealer(object):
    ''' Class to process zabbix triggers and take appropriate actions '''
    def __init__(self):
        self.CONFIG_FILE = '/etc/openshift_tools/remote_healer.conf'
        # Default creds loader
        self._creds_prefix = '/usr/local/bin/autokeys_loader'
        self.load_config()

        self._args = self.parse_args()

        self.setup_logging()
        logging.debug("Got args: " + str(self._args))

    @staticmethod
    def run_cmd(cmd):
        ''' Run passed in command (list-separated arguments) '''
        logging.debug("running: %s", ' '.join(cmd))

        try:
            subprocess.call(cmd)
        except OSError:
            logging.info("failed to run: %s", ' '.join(cmd))

    def cmd_builder(self, cmd):
        ''' Build command with default or user-provided prefix '''
        new_cmd = [self._creds_prefix]
        new_cmd.extend(cmd)
        return new_cmd

    def ossh_cmd(self, host, cmd):
        ''' Build command using ossh as root to specified host '''
        ssh_cmd = ['ossh', host, '-l', 'root', '-c', cmd]
        return self.cmd_builder(ssh_cmd)


    @staticmethod
    def parse_args():
        ''' Parse command line arguments passed in through the
            SSH_ORIGINAL_COMMAND environment variable when READ_SSH is a
            param.
            Also handle when run manually. '''
        my_args = None
        read_ssh_env = False

        # authorized_keys will force direct our command/argv to be
        # 'remote-healer READ_SSH' with the original params stored
        # in SSH_ORIGINAL_COMMAND
        if "READ_SSH" in sys.argv:
            read_ssh_env = True

        parser = argparse.ArgumentParser(description='Take trigger values ' +
                                         'from command line or ' +
                                         'SSH_ORIGINAL_COMMAND and take ' +
                                         'appropriate healing actions')
        parser.add_argument("--host", required=True)
        parser.add_argument("--trigger", required=True)
        parser.add_argument("--trigger-val", required=True)
        parser.add_argument("--verbose", action="store_true", help='Print to stdout')
        parser.add_argument("--debug", action="store_true", help='Log more details')

        if read_ssh_env:
            cmd = os.environ.get("SSH_ORIGINAL_COMMAND", "")

            # SSH_ORIGINAL_COMMAND will include the command part and not just
            # the args. So drop the first lexical token before calling
            # parse_args()
            my_args = parser.parse_args(shlex.split(cmd)[1:])
        else:
            my_args = parser.parse_args()

        return my_args

    def setup_logging(self):
        ''' Configure logging '''
        LOGFILE = "/var/log/remote-healer.log"

        # Default log level
        log_level = logging.INFO

        if self._args.debug:
            log_level = logging.DEBUG

        logging.basicConfig(filename=LOGFILE, format="%(asctime)s %(message)s",
                            level=log_level)
        if self._args.verbose:
            # Print to stdout in addition to log file
            logging.getLogger().addHandler(logging.StreamHandler())

    def load_config(self):
        ''' Setup creds prefix to ensure creds are acquired before trying
            to run a healing action. '''
        config = ConfigParser.ConfigParser()
        config.read(self.CONFIG_FILE)
        if config.has_option('creds', 'loader'):
            self._creds_prefix = config.get('creds', 'loader')

    def validate_host(self):
        ''' Make sure host argument is non-malicious '''
        # Hosts typically have the form of cluster-type-randomid
        # ie. qe-master-a1b2c3 / qe-node-compute-a1b2c3
        # ... there are exceptions: ansible-tower / puppet / use-ctl
        regex = r'^[a-zA-Z0-9]+[a-zA-Z0-9-]*$'
        match = re.search(regex, self._args.host)
        if match is None:
            logging.info("Host: %s doesn't match a know host pattern",
                         self._args.host)
            sys.exit(1)
        self._args.host = match.group(0)

    def main(self):
        ''' Entry point for class '''
        logging.info("host: " + self._args.host + " trigger: " +
                     self._args.trigger + " trigger value: " +
                     self._args.trigger_val)

        # Validate passed in host arg since it will be used for ssh cmds
        self.validate_host()

        #
        # Here we will match on the passed in trigger and take
        # appropriate action.
        # Be sure to have review by Joel Smith when making changes.
        #
        if re.search(r'^\[HEAL\] OVS may not be running on', self._args.trigger):
            logging.info("Restarting OVS on " + self._args.host)

            # Stop OpenShift/docker
            cmd = self.ossh_cmd(self._args.host,
                                'systemctl stop atomic-openshift-node '
                                'atomic-openshift-master docker')
            self.run_cmd(cmd)

            # Restart Open vSwitch
            cmd = self.ossh_cmd(self._args.host, 'systemctl restart openvswitch')
            self.run_cmd(cmd)

            # Start OpenShift/docker
            cmd = self.ossh_cmd(self._args.host,
                                'systemctl start atomic-openshift-master '
                                'atomic-openshift-node docker')
            self.run_cmd(cmd)

            # Start up monitoring
            cmd = self.ossh_cmd(self._args.host,
                                'systemctl start oso-rhel7-host-monitoring')
            self.run_cmd(cmd)

            # Run reporting to quiet down trigger
            cmd = self.ossh_cmd(self._args.host,
                                'docker exec oso-rhe7-host-monitoring /usr/bin/cron-send-ovs-stats')
        elif re.search(r'^\[HEAL\] Critically High Memory usage of  docker  on', self._args.trigger):
            logging.info("Restarting docker on " + self._args.host)

            #run playbook to evacuate the host and restart the docker
            cmd = 'ansible-playbook  /usr/bin/heal_for_docker_use_too_much_memory.yml -e "cli_nodename='+self._args.host+'"'
            #run
            self.run_cmd(cmd.split())

        else:
            logging.info("No healing action defined for trigger: " + self._args.trigger)

if __name__ == '__main__':
    rmt_heal = RemoteHealer()
    rmt_heal.main()
