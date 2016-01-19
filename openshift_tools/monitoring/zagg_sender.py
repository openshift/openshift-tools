#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Collect metrics and send metrics to Zagg.  The data
being send to Zagg is done using REST API using the ZaggClient
module

Examples:

    from openshift_tools.monitoring.zagg_common import ZaggConnection, ZaggHeartbeat
    from openshift_tools.monitoring.zagg_sender import ZaggSender, ZaggHeartbeat
    HOSTNAME = 'use-tower1.ops.rhcloud.com'

    ZAGGCONN = ZaggConnection(url='https://172.17.0.151', user='admin', password='pass')
    ZAGGHEARTBEAT = ZaggHeartbeat(templates=['template1', 'template2'], hostgroups=['hostgroup1', 'hostgroup2'])

    zs = ZaggSender(host=HOSTNAME, zagg_connection=ZAGGCONN)
    zs.add_heartbeat(ZAGGHEARTBEAT)
    zs.add_zabbix_keys({ 'test.key' : '1' })
    zs.send_metrics()
"""

from openshift_tools.monitoring.metricmanager import UniqueMetric
from openshift_tools.monitoring.zagg_client import ZaggClient
from openshift_tools.monitoring.zagg_common import ZaggConnection
import json
import os
import yaml

class ZaggSenderException(Exception):
    '''
        ZabbixSenderException
        Exists to propagate errors up from the api
    '''
    pass

class ZaggSender(object):
    """
    collect and create UniqueMetrics and send them to Zagg
    """

    def __init__(self, host=None, zagg_connection=None, verbose=False, debug=False):
        """
        set up the zagg client and unique_metrics
        """
        self.unique_metrics = []
        self.config = None
        self.config_file = '/etc/openshift_tools/zagg_client.yaml'
        self.verbose = verbose
        self.debug = debug

        if not host:
            host = self.get_default_host()

        if not zagg_connection:
            zagg_connection = self.get_default_zagg_connecton()

        self.host = host
        self.zaggclient = ZaggClient(zagg_connection=zagg_connection)

    def print_unique_metrics_key_value(self):
        """
        This function prints the key/value pairs the UniqueMetrics that ZaggSender
        currently has stored
        """

        print "\nZaggSender Key/Value pairs:"
        print "=============================="
        for unique_metric in self.unique_metrics:
            print("%s:  %s") % (unique_metric.key, unique_metric.value)
        print "==============================\n"

    def print_unique_metrics(self):
        """
        This function prints all of the information of the UniqueMetrics that ZaggSender
        currently has stored
        """

        print "\nZaggSender UniqueMetrics:"
        print "=============================="
        for unique_metric in self.unique_metrics:
            print unique_metric
        print "==============================\n"

    def parse_config(self):
        """ parse default config file """

        if not self.config:
            if not os.path.exists(self.config_file):
                raise ZaggSenderException(self.config_file + " does not exist.")
            self.config = yaml.load(file(self.config_file))

    def get_default_host(self):
        """ get the 'host' value from the config file """
        self.parse_config()

        return self.config['host']['name']

    def get_default_zagg_connecton(self):
        """ get the values and create a zagg_connection """

        self.parse_config()
        zagg_server = self.config['zagg']['url']
        zagg_user = self.config['zagg']['user']
        zagg_password = self.config['zagg']['pass']
        zagg_ssl_verify = self.config['zagg'].get('ssl_verify', False)
        zagg_debug = self.config['zagg'].get('debug', False)

        if isinstance(zagg_ssl_verify, str):
            zagg_ssl_verify = (zagg_ssl_verify == 'True')

        if self.debug:
            zagg_debug = self.debug
        elif isinstance(zagg_debug, str):
            zagg_debug = (zagg_debug == 'True')

        zagg_connection = ZaggConnection(url=zagg_server,
                                         user=zagg_user,
                                         password=zagg_password,
                                         ssl_verify=zagg_ssl_verify,
                                         debug=zagg_debug,
                                        )

        return zagg_connection

    def add_heartbeat(self, heartbeat, host=None):
        """ create a heartbeat unique metric to send to zagg """

        if not host:
            host = self.host

        hb_metric = UniqueMetric.create_heartbeat(host,
                                                  heartbeat.templates,
                                                  heartbeat.hostgroups,
                                                 )
        self.unique_metrics.append(hb_metric)

    def add_zabbix_keys(self, zabbix_keys, host=None):
        """ create unique metric from zabbix key value pair """

        if not host:
            host = self.host

        zabbix_metrics = []

        for key, value in zabbix_keys.iteritems():
            zabbix_metric = UniqueMetric(host, key, value)
            zabbix_metrics.append(zabbix_metric)

        self.unique_metrics += zabbix_metrics

    def add_zabbix_dynamic_item(self, discovery_key, macro_string, macro_array, host=None):
        """
        This creates a dynamic item prototype that is required
        for low level discovery rules in Zabbix.
        This requires:
        - dicovery key
        - macro string
        - macro name

        This will create a zabbix key value pair that looks like:

        disovery_key = "{"data": [
                          {"{#macro_string}":"macro_array[0]"},
                          {"{#macro_string}":"macro_array[1]"},
                        ]}"
        """

        if not host:
            host = self.host

        data_array = [{'{%s}' % macro_string : i} for i in macro_array]
        json_data = json.dumps({'data' : data_array})

        zabbix_dynamic_item = UniqueMetric(host, discovery_key, json_data)

        self.unique_metrics.append(zabbix_dynamic_item)

    def send_metrics(self):
        """
        Send list of Unique Metrics to Zagg
        clear self.unique_metrics
        """
        if self.verbose:
            self.print_unique_metrics_key_value()

        if self.debug:
            self.print_unique_metrics()

        self.zaggclient.add_metric(self.unique_metrics)
        self.unique_metrics = []
