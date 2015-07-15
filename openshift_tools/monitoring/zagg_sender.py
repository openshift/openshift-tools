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
    METRICS = [
        'kernel.all',
        'swap.free',
        'swap.length',
        'swap.used',
        ]

    ZAGGCONN = ZaggConnection(host='172.17.0.151', user='admin', password='pass')
    ZAGGHEARTBEAT = ZaggHeartbeat(templates=['template1', 'template2'], hostgroups=['hostgroup1', 'hostgroup2'])

    zs = ZaggSender(host=HOSTNAME, zagg_connection=ZAGGCONN)
    zs.add_pcp_metrics(METRICS)
    zs.add_heartbeat(ZAGGHEARTBEAT)
    zs.add_zabbix_keys({ 'test.key' : '1' })
    zs.send_metrics()
"""

from openshift_tools.monitoring.zagg_client import ZaggClient
from openshift_tools.monitoring import pminfo
from openshift_tools.monitoring.metricmanager import UniqueMetric

class ZaggSender(object):
    """
    collect and create UniqueMetrics and send them to Zagg
    """

    def __init__(self, host, zagg_connection):
        """
        set up the zagg client, pcp_metrics and unique_metrics
        """
        self.zaggclient = ZaggClient(zagg_connection=zagg_connection)
        self.host = host
        self.unique_metrics = []

    def add_pcp_metrics(self, pcp_metrics, host=None):
        """
        Evaluate a list of metrics from pcp using pminfo
        return list of  UniqueMetrics
        """
        if not host:
            host = self.host

        pcp_metric_dict = pminfo.get_metrics(pcp_metrics)

        for metric, value in pcp_metric_dict.iteritems():
            new_unique_metric = UniqueMetric(host, metric, value)
            self.unique_metrics.append(new_unique_metric)

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

    def send_metrics(self):
        """
        Send list of Unique Metrics to Zagg
        clear self.unique_metrics
        """
        self.zaggclient.add_metric(self.unique_metrics)
        self.unique_metrics = []
