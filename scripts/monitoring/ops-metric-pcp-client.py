#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
"""
ops-metric-pcp-client: Script that sends pcp metrics to metric.

By default this script reads /etc/openshift_tools/metric_server.yaml and sends
the pcp metrics defined in the "pcp" section.  It will also use this config file for
information (name of metric server, hostname of server) needed to send to metric.
These settings can be overridden from the cli.

For more info use:

ops-metric-pcp-client --help


Examples
# Send pcp metrics (looks in a config file to know exactly which metrics to query and send)
ops-metric-pcp-client

# Send additional pcp metrics from the command line:
ops-metric-pcp-client -m  pcp.metric1,pcp.metric2,pcp.metric3

"""

import argparse
from openshift_tools.monitoring import pminfo
from openshift_tools.monitoring.metric_sender import MetricSender
import yaml

class OpsMetricPCPClient(object):
    """ class to send data to metric sender """

    def __init__(self):
        self.metric_sender = None
        self.args = None
        self.config = None
        self.pcp_metrics = []
        self.heartbeat = None

    def run(self):
        """ main function to run the script """

        self.parse_args()
        self.parse_config(self.args.config_file)
        self.config_metric_sender()

        if self.args.metrics:
            self.add_metrics()

        self.add_metrics_from_config()

        self.metric_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='Metric PCP metric sender')
        parser.add_argument('--send-pcp-metrics', help="send pcp metrics", action="store_true")
        parser.add_argument('-m', '--metrics', help="send PCP metrics")
        parser.add_argument('-s', '--host', help='specify host name as registered in Zabbix')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
        parser.add_argument('-c', '--config-file', help='ops-metric-client config file',
                            default='/etc/openshift_tools/metric_sender.yaml')

        self.args = parser.parse_args()

    def parse_config(self, config_file):
        """ parse config file """
        self.config = yaml.load(file(config_file))

    def config_metric_sender(self):
        """ configure the metric_sender """

        metric_verbose = self.args.verbose
        metric_debug = self.args.debug
        host = self.args.host if self.args.host else self.config['host']['name']

        if isinstance(metric_verbose, str):
            metric_verbose = (metric_verbose == 'True')

        if isinstance(metric_debug, str):
            metric_debug = (metric_debug == 'True')

        self.metric_sender = MetricSender(host=host, verbose=metric_verbose, debug=metric_debug,
                                          config_file=self.args.config_file)

    def add_metrics_from_config(self):
        """ collect pcp metrics from a config file. Add to send to MetricSender """

        self.add_pcp_to_metric_sender(self.config['pcp']['metrics'])

    def add_metrics(self):
        """ collect pcp metrics to send to MetricSender """

        metric_list = self.args.metrics.split(',')

        self.add_pcp_to_metric_sender(metric_list)

    def add_pcp_to_metric_sender(self, pcp_metrics):
        """ something pcp yada yada """

        pcp_metric_dict = pminfo.get_metrics(metrics=pcp_metrics, derived_metrics=None)

        self.metric_sender.add_metric(pcp_metric_dict)

if __name__ == "__main__":
    OZPC = OpsMetricPCPClient()
    OZPC.run()
