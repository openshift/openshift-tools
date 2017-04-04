#!/usr/bin/env python
'''
   Command to send data extracted from prometheus endpoints to monitoring systems
   For example config see prometheus_metrics.yml.example in the same folder this script is
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
#If we break the few lines it will be harder to read in this case
#pylint: disable=line-too-long


import argparse
import logging
import sys
import yaml
import requests

from openshift_tools.monitoring.metric_sender import MetricSender
from prometheus_client.parser import text_string_to_metric_families

logger = logging.getLogger()
logger.setLevel(logging.INFO)
consolelog = logging.StreamHandler()
logger.addHandler(consolelog)

class PrometheusMetricSender(object):
    """ class to gather all metrics from prometheus metrics endpoints """

    def __init__(self):
        self.args = None
        self.parser = None
        self.config = None
        self.metric_sender = MetricSender()

    def parse_args(self):
        '''Parse the arguments for this script'''
        self.parser = argparse.ArgumentParser(description="Script that gathers metrics from prometheus endpoints")
        self.parser.add_argument('-d', '--debug', default=False,
                                 action="store_true", help="debug mode")
        self.parser.add_argument('-t', '--test', default=False,
                                 action="store_true", help="Run the script but don't send to monitoring systems")
        self.parser.add_argument('-c', '--configfile', default='/etc/openshift_tools/prometheus_metrics.yml',
                                 help="Config file that contains metrics to be collected, defaults to prometheus_metrics.yml")

        self.args = self.parser.parse_args()

    @staticmethod
    def call_api(rest_path):
        ''' Makes REST call to given url'''
        try:
            response = requests.get(rest_path)
        except requests.exceptions.ConnectionError:
            logger.exception('Error talking to the rest endpoint given: %s', rest_path)
        else:
            return response.content

    def read_metric(self, met):
        ''' read a prometheus endpoint and create data for monitoring systems'''
        return_data = {}
        content = self.call_api(met['url'])
        if content is not None:
            for metric in text_string_to_metric_families(content):
                # skipping histogram and summary types unless we find a good way to add them to zabbix (unlikely)
                if metric.type in ['histogram', 'summary']:
                    continue
                elif metric.type in ['counter', 'gauge']:
                    if metric.name in met['metrics']:
                        zmetric_name = '{}.{}'.format(met['name'], metric.name.replace('_', '.'))
                        logger.debug('Sending: %s - %s', zmetric_name, metric.samples[0][2])
                        return_data[zmetric_name] = metric.samples[0][2]
                    else:
                        logger.debug('We are skipping metric, not requested: %s', metric.name)
                else:
                    logger.error('Unknown metric type: %s - %s', metric.type, metric.name)

        return return_data

    @staticmethod
    def check_endpoint(endpoint_config):
        ''' Just a quick check to make sure the config file has the keys required and they are not empty
            for example, the expected endpoint config should have a valid name, url, and metrics listed
            - name: 'podchecker'
              url: 'http://podchecker.projectawesome.svc.cluster.local:1234/metrics'
              metrics:
              - 'podchecker_awesome_stats'
              - 'podchecker_memory_usage'

            if any of the above config options are not present or empty, PrometheusMetricsSender skips the endpoint
        '''
        for item in set(('name', 'url', 'metrics')):
            if not endpoint_config.get(item):
                return False

        return True

    def run(self):
        ''' Get data from prometheus metrics endpoints
        '''
        self.parse_args()

        if self.args.debug:
            logger.setLevel(logging.DEBUG)

        try:
            with open(self.args.configfile, 'r') as configfile:
                self.config = yaml.safe_load(configfile)
        except IOError:
            logger.exception('There was a problem opening the config file')
            logger.error('Exiting because of above problem')
            sys.exit(1)

        for target in self.config['endpoints']:
            if self.check_endpoint(target):
                self.metric_sender.add_metric(self.read_metric(target))

        self.send_zagg_data()

    def send_zagg_data(self):
        ''' Sending the data to monitoring or displaying it in console when test option is used
        '''
        if not self.args.test:
            self.metric_sender.send_metrics()
        else:
            self.metric_sender.print_unique_metrics()

if __name__ == '__main__':
    PMS = PrometheusMetricSender()
    PMS.run()
