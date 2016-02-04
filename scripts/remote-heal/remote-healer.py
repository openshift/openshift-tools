#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
    Tool to process and take action on incoming zabbix triggers.
'''
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name

import argparse
import ConfigParser
import logging
import re
import subprocess

class RemoteHealer(object):
    ''' Class to process zabbix triggers and take appropriate actions '''
    def __init__(self):
        self.CONFIG_FILE = '/etc/openshift_tools/remote_healer.conf'
        self._creds_prefix = '/usr/local/bin/autokeys_loader'
        self.load_config()
        self._args = self.parse_args()
        self.setup_logging()

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
        ''' Parse command line arguments '''
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", required=True)
        parser.add_argument("--trigger", required=True)
        parser.add_argument("--trigger-val", required=True)
        parser.add_argument("--verbose", action="store_true", help='Print to stdout')
        parser.add_argument("--debug", action="store_true", help='Log more details')
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

    def main(self):
        ''' Entry point for class '''
        logging.info("host: " + self._args.host + " trigger: " + self._args.trigger +
                     " trigger value: " + self._args.trigger_val)

        #
        # Here we will match on the passed in trigger and take appropriate action
        #
        if re.search("^OVS may not be running on", self._args.trigger):
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

        else:
            logging.info("No healing action defined for trigger: " + self._args.trigger)

if __name__ == '__main__':
    rmt_heal = RemoteHealer()
    rmt_heal.main()
