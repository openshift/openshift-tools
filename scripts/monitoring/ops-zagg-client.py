#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
"""
ops-zagg-client: Script that sends metrics to zagg.

This script will send metrics to Zagg.  This script will send:

pcp metrics
heartbeat (registration information)
single zabbix keys.

By default this script reads /etc/openshift_tools/zagg_client.yaml
for information needed to send to zagg.  Some of the settings can be overridden
from the cli.

Examples
# Send pcp metrics (looks in a config file to know exactly which metrics to query and send)
ops-zagg-client --send-pcp-metrics

# Send a heartbeat (looks in a config file for specifics)
ops-zagg-client --send-heartbeat

# Send a single metric (generic interface, send any adhoc metrics)
ops-zagg-client -s hostname.example.com -k zbx.item.name -o someval

# Send a dynamic low level discovery with macros
# low level dynamic objects require:
# - discovery key: This is what was setup and defined in Zabbix in the disovery rule
# - macro string: This is the variable that will be used to setup the item and trigger
# - macro name: This is the name of object.  This is a comma seperated list of names

ops-zagg-client -s --discovery-key filesys --macro-string #FILESYS --macro-names /,/var,/home

"""

import argparse
from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.monitoring.zagg_common import ZaggConnection, ZaggHeartbeat
import yaml

class OpsZaggClient(object):
    """ class to send data to zagg """

    def __init__(self):
        self.zagg_sender = None
        self.args = None
        self.config = None
        self.pcp_metrics = []
        self.heartbeat = None

    def run(self):
        """ main function to run the script """

        self.parse_args()
        self.parse_config(self.args.config_file)
        self.config_zagg_sender()

        if self.args.send_pcp_metrics:
            self.add_pcp_metrics()

        if self.args.send_heartbeat:
            self.add_heartbeat()

        if self.args.key and self.args.value:
            self.add_zabbix_key()

        if self.args.discovery_key and self.args.macro_string and self.args.macro_names:
            self.add_zabbix_dynamic_item()

        self.zagg_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='Zagg metric sender')
        parser.add_argument('--send-pcp-metrics', help="send pcp metrics to zagg", action="store_true")
        parser.add_argument('--send-heartbeat', help="send heartbeat metric to zagg", action="store_true")
        parser.add_argument('-s', '--host', help='specify host name as registered in Zabbix')
        parser.add_argument('-z', '--zagg-url', help='url of Zagg server')
        parser.add_argument('--zagg-user', help='username of the Zagg server')
        parser.add_argument('--zagg-pass', help='Password of the Zagg server')
        parser.add_argument('--zagg-ssl-verify', default=False, help='Whether to verify ssl certificates.')
        parser.add_argument('-c', '--config-file', help='ops-zagg-client config file',
                            default='/etc/openshift_tools/zagg_client.yaml')

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

    def config_zagg_sender(self):
        """ configure the zagg_sender """

        zagg_url = self.args.zagg_url if self.args.zagg_url else self.config['zagg']['url']
        zagg_user = self.args.zagg_user if self.args.zagg_user else self.config['zagg']['user']
        zagg_password = self.args.zagg_pass if self.args.zagg_pass else self.config['zagg']['pass']

        zagg_ssl_verify = self.config['zagg'].get('ssl_verify', False)

        if isinstance(zagg_ssl_verify, str):
            zagg_ssl_verify = (zagg_ssl_verify == 'True')

        if self.args.zagg_ssl_verify:
            zagg_ssl_verify = self.args.zagg_ssl_verify

        zagg_conn = ZaggConnection(url=zagg_url,
                                   user=zagg_user,
                                   password=zagg_password,
                                   ssl_verify=zagg_ssl_verify,
                                  )

        host = self.args.host if self.args.host else self.config['host']['name']
        self.zagg_sender = ZaggSender(host, zagg_conn)

    def add_heartbeat(self):
        """ crate a hearbeat metric """
        heartbeat = ZaggHeartbeat(templates=self.config['heartbeat']['templates'],
                                  hostgroups=self.config['heartbeat']['hostgroups'],
                                 )
        self.zagg_sender.add_heartbeat(heartbeat)

    def add_pcp_metrics(self):
        """ collect pcp metrics to send to ZaggSender """

        self.zagg_sender.add_pcp_metrics(self.config['pcp']['metrics'])

    def add_zabbix_key(self):
        """ send zabbix key/value pair to zagg """

        self.zagg_sender.add_zabbix_keys({self.args.key : self.args.value})

    def add_zabbix_dynamic_item(self):
        """ send zabbix low level discovery item to zagg """

        self.zagg_sender.add_zabbix_dynamic_item(self.args.discovery_key,
                                                 self.args.macro_string,
                                                 self.args.macro_names.split(','),
                                                )
if __name__ == "__main__":
    OZC = OpsZaggClient()
    OZC.run()
