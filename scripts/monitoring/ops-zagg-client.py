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

        self.zagg_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='Zagg metric sender')
        parser.add_argument('--send-pcp-metrics', help="send pcp metrics to zagg", action="store_true")
        parser.add_argument('--send-heartbeat', help="send heartbeat metric to zagg", action="store_true")
        parser.add_argument('-s', '--host', help='specify host name as registered in Zabbix')
        parser.add_argument('-z', '--zagg-server', help='hostname of IP of Zagg server')
        parser.add_argument('--zagg-user', help='username of the Zagg server')
        parser.add_argument('--zagg-pass', help='password of the Zagg server')
        parser.add_argument('-k', '--key', help='zabbix key')
        parser.add_argument('-o', '--value', help='zabbix value')
        parser.add_argument('-c', '--config-file', help='ops-zagg-client config file',
                            default='/etc/openshift_tools/zagg_client.yaml')
        self.args = parser.parse_args()

    def parse_config(self, config_file):
        """ parse config file """
        self.config = yaml.load(file(config_file))

    def config_zagg_sender(self):
        """ configure the zagg_sender """

        zagg_server = self.args.zagg_server if self.args.zagg_server else self.config['zagg']['host']
        zagg_user = self.args.zagg_user if self.args.zagg_user else self.config['zagg']['user']
        zagg_password = self.args.zagg_pass if self.args.zagg_pass else self.config['zagg']['pass']
        zagg_ssl_verify = self.args.zagg_pass if self.args.zagg_pass else self.config['zagg']['ssl_verify']
        host = self.args.host if self.args.host else self.config['host']['name']

        zagg_conn = ZaggConnection(host=zagg_server,
                                   user=zagg_user,
                                   password=zagg_password,
                                   ssl_verify=zagg_ssl_verify,
                                  )

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

if __name__ == "__main__":
    OZC = OpsZaggClient()
    OZC.run()
