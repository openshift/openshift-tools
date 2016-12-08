#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
"""
ops-zagg-pcp-client: Script that sends pcp metrics to zagg.

By default this script reads /etc/openshift_tools/zagg_client.yaml and sends
the pcp metrics defined in the "pcp" section.  It will also use this config file for
information (name of zagg server, hostname of server) needed to send to zagg.
These settings can be overridden from the cli.

For more info use:

ops-zagg-pcp-client --help


Examples
# Send pcp metrics (looks in a config file to know exactly which metrics to query and send)
ops-zagg-pcp-client

# Send additional pcp metrics from the command line:
ops-zagg-pcp-client -m  pcp.metric1,pcp.metric2,pcp.metric3

"""

import argparse
from openshift_tools.monitoring import pminfo
from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.monitoring.zagg_common import ZaggConnection
import yaml

class OpsZaggPCPClient(object):
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

        if self.args.metrics:
            self.add_metrics()

        self.add_metrics_from_config()

        self.zagg_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='Zagg PCP metric sender')
        parser.add_argument('--send-pcp-metrics', help="send pcp metrics to zagg", action="store_true")
        parser.add_argument('-m', '--metrics', help="send PCP metrics to zagg")
        parser.add_argument('-s', '--host', help='specify host name as registered in Zabbix')
        parser.add_argument('-z', '--zagg-url', help='url of Zagg server')
        parser.add_argument('--zagg-user', help='username of the Zagg server')
        parser.add_argument('--zagg-pass', help='Password of the Zagg server')
        parser.add_argument('--zagg-ssl-verify', default=None, help='Whether to verify ssl certificates.')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
        parser.add_argument('-c', '--config-file', help='ops-zagg-client config file',
                            default='/etc/openshift_tools/zagg_client.yaml')

        self.args = parser.parse_args()

    def parse_config(self, config_file):
        """ parse config file """
        self.config = yaml.load(file(config_file))

    def config_zagg_sender(self):
        """ configure the zagg_sender """

        zagg_url = self.args.zagg_url if self.args.zagg_url else self.config['zagg']['url']
        zagg_user = self.args.zagg_user if self.args.zagg_user else self.config['zagg']['user']
        zagg_password = self.args.zagg_pass if self.args.zagg_pass else self.config['zagg']['pass']
        zagg_verbose = self.args.verbose if self.args.verbose else self.config['zagg']['verbose']
        zagg_debug = self.args.debug if self.args.debug else self.config['zagg']['debug']
        zagg_ssl_verify = self.args.zagg_ssl_verify if self.args.zagg_ssl_verify else self.config['zagg']['ssl_verify']
        host = self.args.host if self.args.host else self.config['host']['name']

        if isinstance(zagg_verbose, str):
            zagg_verbose = (zagg_verbose == 'True')

        if isinstance(zagg_debug, str):
            zagg_debug = (zagg_debug == 'True')

        if isinstance(zagg_ssl_verify, str):
            zagg_ssl_verify = (zagg_ssl_verify == 'True')

        zagg_conn = ZaggConnection(url=zagg_url,
                                   user=zagg_user,
                                   password=zagg_password,
                                   ssl_verify=zagg_ssl_verify,
                                   debug=zagg_debug,
                                  )

        self.zagg_sender = ZaggSender(host, zagg_conn, zagg_verbose, zagg_debug)

    def add_metrics_from_config(self):
        """ collect pcp metrics from a config file. Add to send to ZaggSender """

        self.add_pcp_to_zagg_sender(self.config['pcp']['metrics'])

    def add_metrics(self):
        """ collect pcp metrics to send to ZaggSender """

        metric_list = self.args.metrics.split(',')

        self.add_pcp_to_zagg_sender(metric_list)

    def add_pcp_to_zagg_sender(self, pcp_metrics):
        """ something pcp yada yada """

        pcp_metric_dict = pminfo.get_metrics(metrics=pcp_metrics, derived_metrics=None)

        self.zagg_sender.add_zabbix_keys(pcp_metric_dict)

if __name__ == "__main__":
    OZPC = OpsZaggPCPClient()
    OZPC.run()
