#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
# pylint flaggs import errors, as the bot doesn't know have openshift-tools libs
#pylint: disable=import-error
"""
ops-hawk-client: Script that sends metrics to hawk.

This script will send metrics to Hawk.  This script will send:

heartbeat (registration information)
single zabbix keys.

By default this script reads /etc/openshift_tools/hawk_client.yaml
for information needed to send to hawk.  Some of the settings can be overridden
from the cli.

Examples
# Send a heartbeat (looks in a config file for specifics)
ops-hawk-client --send-heartbeat

# Send a single metric (generic interface, send any adhoc metrics)
ops-hawk-client -s hostname.example.com -k zbx.item.name -o someval

"""

import argparse
from openshift_tools.monitoring.hawk_sender import HawkSender
from openshift_tools.monitoring.hawk_common import HawkConnection, HawkHeartbeat
import yaml

class OpsHawkClient(object):
    """ class to send data to hawk """

    def __init__(self):
        self.hawk_sender = None
        self.args = None
        self.config = None
        self.heartbeat = None

    def run(self):
        """ main function to run the script """

        self.parse_args()
        self.parse_config(self.args.config_file)
        self.config_hawk_sender()

        if self.args.send_heartbeat:
            self.add_heartbeat()

        if self.args.key and self.args.value:
            self.add_zabbix_key()

        if self.args.discovery_key and self.args.macro_string and self.args.macro_names:
            self.add_zabbix_dynamic_item()

        self.hawk_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='Hawk metric sender')
        parser.add_argument('--send-heartbeat', help="send heartbeat metric to hawk", action="store_true")

        group = parser.add_mutually_exclusive_group()
        group.add_argument('-s', '--host',
                           help='specify host name as registered in Zabbix')
        group.add_argument('--synthetic', default=False, action='store_true',
                           help='send as cluster-wide synthetic host')

        parser.add_argument('-z', '--hawk-url', help='url of Hawk server')
        parser.add_argument('--hawk-user', help='username of the Hawk server')
        parser.add_argument('--hawk-pass', help='Password of the Hawk server')
        parser.add_argument('--hawk-ssl-verify', default=None, help='Whether to verify ssl certificates.')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
        parser.add_argument('-c', '--config-file', help='ops-hawk-client config file',
                            default='/etc/openshift_tools/hawk_client.yaml')

        key_value_group = parser.add_argument_group('Sending a Key-Value Pair')
        key_value_group.add_argument('-k', '--key', help='zabbix key')
        key_value_group.add_argument('-o', '--value', help='zabbix value')

        low_level_discovery_group = parser.add_argument_group('Sending a Low Level Discovery Item')
        low_level_discovery_group.add_argument('--discovery-key', help='discovery key')
        low_level_discovery_group.add_argument('--macro-string', help='macro string')
        low_level_discovery_group.add_argument('--macro-names', help='comma separated list of macro names')

        self.args = parser.parse_args()

    def parse_config(self, config_file):
        """ parse config file """
        self.config = yaml.load(file(config_file))

    def config_hawk_sender(self):
        """ configure the hawk_sender """

        hawk_url = self.args.hawk_url if self.args.hawk_url else self.config['hawk']['url']
        hawk_user = self.args.hawk_user if self.args.hawk_user else self.config['hawk']['user']
        hawk_password = self.args.hawk_pass if self.args.hawk_pass else self.config['hawk']['pass']
        hawk_verbose = self.args.verbose if self.args.verbose else self.config['hawk']['verbose']
        hawk_debug = self.args.debug if self.args.debug else self.config['hawk']['debug']
        hawk_ssl_verify = self.args.hawk_ssl_verify if self.args.hawk_ssl_verify else self.config['hawk']['ssl_verify']
        if self.args.host:
            host = self.args.host
        elif self.args.synthetic:
            host = self.config['synthetic_clusterwide']['host']['name']
        else:
            host = self.config['host']['name']

        if isinstance(hawk_verbose, str):
            hawk_verbose = (hawk_verbose == 'True')

        if isinstance(hawk_debug, str):
            hawk_debug = (hawk_debug == 'True')

        if isinstance(hawk_ssl_verify, str):
            hawk_ssl_verify = (hawk_ssl_verify == 'True')

        hawk_conn = HawkConnection(url=hawk_url,
                                   user=hawk_user,
                                   password=hawk_password,
                                   ssl_verify=hawk_ssl_verify,
                                   debug=hawk_debug,
                                  )

        self.hawk_sender = HawkSender(host, hawk_conn, hawk_verbose, hawk_debug)

    def add_heartbeat(self):
        """ crate a hearbeat metric """
        if self.args.synthetic:
            heartbeat = HawkHeartbeat(templates=self.config['synthetic_clusterwide']['heartbeat']['templates'],
                                      hostgroups=self.config['heartbeat']['hostgroups'],
                                     )
        else:
            heartbeat = HawkHeartbeat(templates=self.config['heartbeat']['templates'],
                                      hostgroups=self.config['heartbeat']['hostgroups'],
                                     )
        self.hawk_sender.add_heartbeat(heartbeat)

    def add_zabbix_key(self):
        """ send zabbix key/value pair to hawk """

        self.hawk_sender.add_zabbix_keys({self.args.key : self.args.value})

    def add_zabbix_dynamic_item(self):
        """ send zabbix low level discovery item to hawk """

        #TODO: implement add_zabbix_dynamic_item
        #self.hawk_sender.add_zabbix_dynamic_item(self.args.discovery_key,
        #                                         self.args.macro_string,
        #                                         self.args.macro_names.split(','),
        #                                        )
        pass

if __name__ == "__main__":
    OZC = OpsHawkClient()
    OZC.run()
