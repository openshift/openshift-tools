#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Collect metrics and send metrics to Hawk.  The data
being send to Hawk is done using REST API using the HawkClient
module

Examples:

    from openshift_tools.monitoring.hawk_common import HawkConnection, HawkHeartbeat
    from openshift_tools.monitoring.hawk_sender import HawkSender
    HOSTNAME = 'use-tower1.ops.rhcloud.com'

    ZAGGCONN = HawkConnection(url='https://172.17.0.151', user='admin', password='pass')
    ZAGGHEARTBEAT = HawkHeartbeat(templates=['template1', 'template2'], hostgroups=['hostgroup1', 'hostgroup2'])

    zs = HawkSender(host=HOSTNAME, hawk_connection=ZAGGCONN)
    zs.add_heartbeat(ZAGGHEARTBEAT)
    zs.add_zabbix_keys({ 'test.key' : '1' })
    zs.send_metrics()
"""

from openshift_tools.monitoring.metricmanager import UniqueMetric
from openshift_tools.monitoring.hawk_client import HawkClient
from openshift_tools.monitoring.hawk_common import HawkConnection
import json
import os
import yaml

class HawkSenderException(Exception):
    '''
        HawkSenderException
        Exists to propagate errors up from the api
    '''
    pass

class HawkSender(object):
    """
    collect and create UniqueMetrics and send them to Hawk
    """

    def __init__(self, host=None, hawk_connection=None, verbose=False, debug=False):
        """
        set up the hawk client and unique_metrics
        """
        self.unique_metrics = []
        self.config = None
        self.config_file = '/etc/openshift_tools/hawk_client.yaml'
        self.verbose = verbose
        self.debug = debug

        if not host:
            host = self.get_default_host()

        if not hawk_connection:
            hawk_connection = self.get_default_hawk_connecton()

        self.host = host
        self.hawkclient = HawkClient(hawk_connection=hawk_connection)

    def print_unique_metrics_key_value(self):
        """
        This function prints the key/value pairs the UniqueMetrics that HawkSender
        currently has stored
        """

        print "\nHawkSender Key/Value pairs:"
        print "=============================="
        for unique_metric in self.unique_metrics:
            print("%s:  %s") % (unique_metric.key, unique_metric.value)
        print "==============================\n"

    def print_unique_metrics(self):
        """
        This function prints all of the information of the UniqueMetrics that HawkSender
        currently has stored
        """

        print "\nHawkSender UniqueMetrics:"
        print "=============================="
        for unique_metric in self.unique_metrics:
            print unique_metric
        print "==============================\n"

    def parse_config(self):
        """ parse default config file """

        if not self.config:
            if not os.path.exists(self.config_file):
                raise HawkSenderException(self.config_file + " does not exist.")
            self.config = yaml.load(file(self.config_file))

    def get_default_host(self):
        """ get the 'host' value from the config file """
        self.parse_config()

        return self.config['host']['name']

    def get_default_hawk_connecton(self):
        """ get the values and create a hawk_connection """

        self.parse_config()
        hawk_server = self.config['hawk']['url']
        hawk_user = self.config['hawk']['user']
        hawk_password = self.config['hawk']['pass']
        hawk_ssl_verify = self.config['hawk'].get('ssl_verify', False)
        hawk_debug = self.config['hawk'].get('debug', False)

        if isinstance(hawk_ssl_verify, str):
            hawk_ssl_verify = (hawk_ssl_verify == 'True')

        if self.debug:
            hawk_debug = self.debug
        elif isinstance(hawk_debug, str):
            hawk_debug = (hawk_debug == 'True')

        hawk_connection = HawkConnection(url=hawk_server,
                                         user=hawk_user,
                                         password=hawk_password,
                                         ssl_verify=hawk_ssl_verify,
                                         debug=hawk_debug,
                                        )

        return hawk_connection

    def add_heartbeat(self, heartbeat, host=None):
        """ create a heartbeat unique metric to send to hawk """

        if not host:
            host = self.host

        hb_metric = UniqueMetric.create_heartbeat(host,
                                                  heartbeat.templates,
                                                  heartbeat.hostgroups,
                                                 )
        self.unique_metrics.append(hb_metric)

    def add_zabbix_keys(self, zabbix_keys, host=None, synthetic=False):
        """ create unique metric from zabbix key value pair """

        if synthetic and not host:
            host = self.config['synthetic_clusterwide']['host']['name']
        elif not host:
            host = self.host

        zabbix_metrics = []

        for key, value in zabbix_keys.iteritems():
            zabbix_metric = UniqueMetric(host, key, value)
            zabbix_metrics.append(zabbix_metric)

        self.unique_metrics += zabbix_metrics

    # Allow for 6 arguments (including 'self')
    # pylint: disable=too-many-arguments
    def add_zabbix_dynamic_item(self, discovery_key, macro_string, macro_array, host=None, synthetic=False):
        """
        This creates a dynamic item prototype that is required
        for low level discovery rules in Hawkular.
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

        if synthetic and not host:
            host = self.config['synthetic_clusterwide']['host']['name']
        elif not host:
            host = self.host

        data_array = [{'{%s}' % macro_string : i} for i in macro_array]
        json_data = json.dumps({'data' : data_array})

        zabbix_dynamic_item = UniqueMetric(host, discovery_key, json_data)

        self.unique_metrics.append(zabbix_dynamic_item)

    def send_metrics(self):
        """
        Send list of Unique Metrics to Hawk
        clear self.unique_metrics
        """
        if self.verbose:
            self.print_unique_metrics_key_value()

        if self.debug:
            self.print_unique_metrics()

        self.hawkclient.add_metric(self.unique_metrics)
        self.unique_metrics = []
