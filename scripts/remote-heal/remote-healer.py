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

    def get_instance_info(self, nodename):
        #run command to get the host info
        s = subprocess.check_output('/etc/ansible/inventory/multi_inventory.py', shell=True)

        s_json = json.loads(s)

        #print s_json
        hostinfo = None

        if s_json['_meta']['hostvars'].has_key(hostname):
            hostinfo = s_json['_meta']['hostvars'][hostname]
        else:
            pass

        return hostinfo

    def get_readytorun(self, filepath)
    #check if there any auto-heal on this cluster in 30 mintes
        readytorun = False
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            create_time = stat.st_birthtime
            now = datetime.datetime.now()
            #if there is no auto-heal for this cluster in 30 minutes , set the readytorun to true
            if (now-create_time).seconds > 1800:
                readytorun = True
                os.remove(file_path)
                file = open(filepath,'w')

        else:
            file = open(filepath,'w')
            readytorun = True

        return readytorun

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
        elif re.search(r'^\[Heal\] Critically High Memory usage of  docker  on', self._args.trigger):
            logging.info("Restarting docker on " + self._args.host)

            #run playbook to evacuate the host and restart the docker
            cmd = 'ansible-playbook  /usr/bin/heal_for_docker_use_too_much_memory.yml -e "cli_nodename='+self._args.host+'"'
            #run
            self.run_cmd(cmd.split())

        elif re.search(r'^\[Heal\] Filesystem: /dev/mapper/rootvg-var has less than 1[05]% free disk space on', self._args.trigger):
            logging.info("Cleaningup /var on " + self._args.host)
            # run the playbook to cleanup the log files
            cmd = '/usr/local/bin/autokeys_loader ansible-playbook /usr/bin/heal_cleanup_rootvg-var.yml -e cli_tag_name=' + self._args.host
            self.run_cmd(cmd.split())

        elif re.search(r'^\[Heal\] Heartbeat.ping has failed (5min) on ', self._args.trigger):
            logging.info("Auto heal for heartbeat.ping on " + self._args.host)
            #get all the needed info from the hostname including: cluster_id,account_id,instance_id
            hostinfo = self.get_instance_info(self._args.trigger)
            #if we could get the info
            if hostinfo:
                cluster_id = hostinfo['ec2_tag_clusterid']
                account_id = hostinfo['oo_accountid']
                instance_id = hostinfo['ec2_id']
                # check the cluster lock file see if this cluster already have some instance auto-heal run in 30 minutes
                filepath = '/tmp/auto-heal-lock-'+cluster_id
                readytorun = self.get_readytorun(filepath)
                #to run the create cred part
                if readytorun:
                    cmd_cred = '/path/need/fix/refresh_aws_tmp_credentials.py --aws-account_id '+account_id+' --aws-account_name '+cluster_id+'      --aws-credentials-file ~/.aws/credentials.tmp --idp-host login.ops.openshift.com'
                    self.run_cmd(cmd_cred.split())
                    #after get the cred , run the playbook
                    cmd = 'ansible-playbook  /usr/bin/heal_for_heartbeat.yml -e "cli_nodename='+self._args.host+'" -e "cluster_id='+cluster_id+'"'
                    self.run_cmd(cmd.split())
                    

        else:
            logging.info("No healing action defined for trigger: " + self._args.trigger)

if __name__ == '__main__':
    rmt_heal = RemoteHealer()
    rmt_heal.main()
