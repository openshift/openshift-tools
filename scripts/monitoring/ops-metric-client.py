#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
# pylint flaggs import errors, as the bot doesn't know have openshift-tools libs
#pylint: disable=import-error
"""
ops-metric-client: Script that sends metrics to through metric_sender.

This script will send metrics to Zagg & Hawk according to which client is active.
This script will send:

heartbeat (registration information)
single metric.

By default this script reads /etc/openshift_tools/metric_sender.yaml
A different config file can be set from the cli

Examples
# Send a heartbeat (looks in a config file for specifics)
ops-metric-client --send-heartbeat

# Send a single metric (generic interface, send any adhoc metrics)
ops-metric-client -s hostname.example.com -k zbx.item.name -o someval

# Send a dynamic low level discovery with macros
# low level dynamic objects require:
# - discovery key: This is what was setup and defined in Zabbix in the disovery rule
# - macro string: This is the variable that will be used to setup the item and trigger
# - macro name: This is the name of object.  This is a comma seperated list of names

ops-metric-client -s --discovery-key filesys --macro-string #FILESYS --macro-names /,/var,/home

"""

import argparse
from openshift_tools.monitoring.metric_sender import MetricSender, MetricSenderHeartbeat
import yaml

class OpsMetricClient(object):
    """ class to send data via MeticSender """

    def __init__(self):
        self.metric_sender = None
        self.args = None
        self.config = None
        self.heartbeat = None

    def run(self):
        """ main function to run the script """

        self.parse_args()
        self.parse_config(self.args.config_file)
        self.config_metric_sender()

        if self.args.send_heartbeat:
            self.add_heartbeat()

        if self.args.key and self.args.value:
            self.add_metric()

        if self.args.discovery_key and self.args.macro_string and self.args.macro_names:
            self.add_dynamic_metric()

        self.metric_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='metric sender')
        parser.add_argument('--send-heartbeat', help="send heartbeat metric to zagg", action="store_true")

        group = parser.add_mutually_exclusive_group()
        group.add_argument('-s', '--host',
                           help='specify host name as registered in Zabbix')
        group.add_argument('--synthetic', default=False, action='store_true',
                           help='send as cluster-wide synthetic host')

        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
        parser.add_argument('-c', '--config-file', help='ops-metric-client config file',
                            default='/etc/openshift_tools/metric_sender.yaml')

        key_value_group = parser.add_argument_group('Sending a Key-Value Pair')
        key_value_group.add_argument('-k', '--key', help='metric key')
        key_value_group.add_argument('-o', '--value', help='metric value')
        key_value_group.add_argument('-t', '--tags', help='list of space delimited key tags: units=byte ...', nargs='*')

        low_level_discovery_group = parser.add_argument_group('Sending a Low Level Discovery Item')
        low_level_discovery_group.add_argument('--discovery-key', help='discovery key')
        low_level_discovery_group.add_argument('--macro-string', help='macro string')
        low_level_discovery_group.add_argument('--macro-names', help='comma separated list of macro names')

        self.args = parser.parse_args()

    def parse_config(self, config_file):
        """ parse config file """
        self.config = yaml.load(file(config_file))

    def config_metric_sender(self):
        """ configure the metric_sender """

        if self.args.host:
            host = self.args.host
        elif self.args.synthetic:
            host = self.config['synthetic_clusterwide']['host']['name']
        else:
            host = self.config['host']['name']

        metric_verbose = self.args.verbose
        metric_debug = self.args.debug
        if isinstance(metric_verbose, str):
            metric_verbose = (metric_verbose == 'True')

        if isinstance(metric_debug, str):
            metric_debug = (metric_debug == 'True')

        self.metric_sender = MetricSender(host=host, verbose=metric_verbose, debug=metric_debug,
                                          config_file=self.args.config_file)

    def add_heartbeat(self):
        """ crate a heartbeat metric """
        if self.args.synthetic:
            heartbeat = MetricSenderHeartbeat(templates=self.config['synthetic_clusterwide']['heartbeat']['templates'],
                                              hostgroups=self.config['heartbeat']['hostgroups'])
        else:
            heartbeat = MetricSenderHeartbeat(templates=self.config['heartbeat']['templates'],
                                              hostgroups=self.config['heartbeat']['hostgroups'])
        self.metric_sender.add_heartbeat(heartbeat)

    def add_metric(self):
        """ send key/value pair """

        # Get tags from command line args
        tags = dict([i.split("=")[0], i.split("=")[1]] for i in self.args.tags) if self.args.tags else {}

        self.metric_sender.add_metric({self.args.key : self.args.value}, key_tags=tags)

    def add_dynamic_metric(self):
        """ send zabbix low level discovery item to zagg """

        self.metric_sender.add_dynamic_metric(self.args.discovery_key,
                                              self.args.macro_string,
                                              self.args.macro_names.split(','))
if __name__ == "__main__":
    OMC = OpsMetricClient()
    OMC.run()
