#!/usr/bin/env python
'''
   Command to send status of etcd to zabbix
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
#If we break the few lines it will be harder to read in this case
#pylint: disable=line-too-long


import argparse
import json
import sys
import yaml
import requests

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender
from prometheus_client.parser import text_string_to_metric_families

class EtcdStatusZaggSender(object):
    """ class to gather all metrics from etcd daemons """

    def __init__(self):
        self.api_host = None
        self.args = None
        self.parser = None
        self.config = None
        self.etcd_ping = 0
        self.default_config = '/etc/openshift_tools/etcd_metrics.yaml'
        self.zagg_sender = ZaggSender()

    def parse_args(self):
        '''Parse the arguments for this script'''
        self.parser = argparse.ArgumentParser(description="Script that gathers metrics from etcd")
        self.parser.add_argument('-d', '--debug', default=False,
                                 action="store_true", help="debug mode")
        self.parser.add_argument('-v', '--verbose', default=False,
                                 action="store_true", help="Verbose?")
        self.parser.add_argument('-t', '--test', default=False,
                                 action="store_true", help="Run the script but don't send to zabbix")
        self.parser.add_argument('-c', '--configfile', default=self.default_config,
                                 help="Config file that contains metrics to be collected, defaults to etcd_metrics.yml")

        self.args = self.parser.parse_args()

    def call_etcd_api(self, rest_path):
        '''Makes the API calls to rest endpoints in etcd'''
        try:
            response = requests.get(self.api_host + rest_path,
                                    cert=(self.config['etcd_info']['files']['ssl_client_cert'],
                                          self.config['etcd_info']['files']['ssl_client_key']),
                                    verify=False)
            self.etcd_ping = 1
        except requests.exceptions.ConnectionError as ex:
            print "ERROR talking to etcd API: {0}".format(ex.message)
        else:
            return response.content

    def json_metric(self, met):
        '''process json data from etcd'''
        return_data = {}
        api_response = self.call_etcd_api(met['path'])
        if api_response:
            content = json.loads(api_response.json())

            for item in met['values']:
                return_data[self.config['etcd_info']['common']['prefix'] + item['zab_key']] = content[item['src']]

        return return_data

    def text_metric(self, met):
        '''process text value from etcd'''
        return_data = {}
        dyn_keys = []

        content = self.call_etcd_api(met['path'])
        if content:
            for metric in text_string_to_metric_families(content):
                # skipping histogram and summary types unless we find a good way to add them to zabbix (unlikely)
                if metric.type in ['histogram', 'summary']:
                    continue
                elif metric.type in ['counter', 'gauge'] and metric.name in met['values']:
                    zab_metric_name = metric.name.replace('_', '.')
                    return_data['metrics.etcd.name[{0}]'.format(zab_metric_name)] = zab_metric_name
                    if len(metric.samples) > 1:
                        if met['values'][metric.name]:
                            sub_key = met['values'][metric.name]
                        for singlemetric in metric.samples:
                            return_data['metrics.etcd[{0}.{1}]'.format(zab_metric_name, singlemetric[1][sub_key])] = singlemetric[2]
                            dyn_keys.append(zab_metric_name + '.' + singlemetric[1][sub_key])
                    else:
                        return_data['metrics.etcd[{0}]'.format(zab_metric_name)] = metric.samples[0][2]
                        dyn_keys.append(zab_metric_name)
                else:
                    if self.args.debug:
                        print 'Got unknown type of metric from etcd, skipping it: ({0}) '.format(metric.type)

        return return_data, dyn_keys

    def run(self):
        ''' Get data from etcd API
        '''
        self.parse_args()

        try:
            with open(self.args.configfile, 'r') as configfile:
                self.config = yaml.load(configfile)
        except IOError as ex:
            print 'There was a problem opening the config file: {0}'.format(ex)
            print 'Exiting'
            sys.exit(1)

        # find out the etcd port
        try:
            with open(self.config['etcd_info']['files']['openshift_master_config'], 'r') as f:
                om_config = yaml.load(f)
        except IOError as ex:
            print 'Problem opening openshift master config: {0}'.format(ex)
            sys.exit(2)
        else:
            self.api_host = om_config["etcdClientInfo"]["urls"][0]

        # let's get the metrics
        for metric in self.config['etcd_info']['metrics']:
            if metric['type'] == 'text':
                zkeys, dynamic_keys = self.text_metric(metric)
                if zkeys and dynamic_keys:
                    self.zagg_sender.add_zabbix_dynamic_item('metrics.etcd', '#ETCD_METRIC', dynamic_keys)
                    self.zagg_sender.add_zabbix_keys(zkeys)
            elif metric['type'] == 'json':
                self.zagg_sender.add_zabbix_keys(self.json_metric(metric))

        self.send_zagg_data()

    def send_zagg_data(self):
        ''' Sending the data to zagg or displaying it in console when test option is used
        '''
        self.zagg_sender.add_zabbix_keys({'openshift.master.etcd.ping' : self.etcd_ping})

        if not self.args.test:
            self.zagg_sender.send_metrics()
        else:
            self.zagg_sender.print_unique_metrics()

if __name__ == '__main__':
    ESZS = EtcdStatusZaggSender()
    ESZS.run()
