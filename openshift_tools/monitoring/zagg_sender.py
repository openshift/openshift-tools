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

import json
from openshift_tools.monitoring.metricmanager import UniqueMetric
from openshift_tools.monitoring.zagg_client import ZaggClient
from openshift_tools.monitoring.zagg_common import ZaggConnection
from openshift_tools.monitoring.generic_metric_sender import GenericMetricSender

class ZaggSender(GenericMetricSender):
    """
    collect and create UniqueMetrics and send them to Zagg
    """

    # Allow for 6 arguments (including 'self')
    # pylint: disable=too-many-arguments
    def __init__(self, host=None, zagg_connection=None, verbose=False, debug=False, config_file=None):
        """
        set up the zagg client and unique_metrics
        """
        super(ZaggSender, self).__init__()

        if not config_file:
            config_file = '/etc/openshift_tools/zagg_client.yaml'

        self.config_file = config_file
        self.unique_metrics = []
        self.verbose = verbose
        self.debug = debug

        if not host:
            host = self.get_default_host()

        if not zagg_connection:
            zagg_connection = self.get_default_zagg_connection()

        self.host = host
        self.zaggclient = ZaggClient(zagg_connection=zagg_connection)

    def get_default_host(self):
        """ get the 'host' value from the config file """
        self.parse_config()

        return self.config['host']['name']

    def get_default_zagg_connection(self):
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

    def add_metric(self, metrics, host=None, synthetic=False):
        """ create unique metric from zabbix key value pair """

        if synthetic and not host:
            host = self.config['synthetic_clusterwide']['host']['name']
        elif not host:
            host = self.host

        zabbix_metrics = []

        for key, value in metrics.iteritems():
            zabbix_metric = UniqueMetric(host, key, value)
            zabbix_metrics.append(zabbix_metric)

        self.unique_metrics += zabbix_metrics

    # Temporary wrapper for add_metric to support old calls to zagg_sender
    def add_zabbix_keys(self, metrics, host=None, synthetic=False):
        """ Temporary wrapper for add_metric to support old calls to zagg_sender """
        self.add_metric(metrics, host, synthetic)


    # Allow for 6 arguments (including 'self')
    # pylint: disable=too-many-arguments
    def add_dynamic_metric(self, discovery_key, macro_string, macro_array, host=None, synthetic=False):
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

        if synthetic and not host:
            host = self.config['synthetic_clusterwide']['host']['name']
        elif not host:
            host = self.host

        data_array = [{'{%s}' % macro_string : i} for i in macro_array]
        json_data = json.dumps({'data' : data_array})

        zabbix_dynamic_item = UniqueMetric(host, discovery_key, json_data)

        self.unique_metrics.append(zabbix_dynamic_item)

    # Temporary wrapper for add_dynamic_metric to support old calls to zagg_sender.
    # Allow for 6 arguments (including 'self')
    # pylint: disable=too-many-arguments
    def add_zabbix_dynamic_item(self, discovery_key, macro_string, macro_array, host=None, synthetic=False):
        """ Temporary wrapper for add_dynamic_metric to support old calls to zagg_sender """
        self.add_dynamic_metric(discovery_key, macro_string, macro_array, host, synthetic)

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
