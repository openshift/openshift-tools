#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Collect data from PCP and send it to Zagg.  The data
being send to Zagg is done using REST API using the ZaggClient
module

Examples:

    from openshift_tools.monitoring.zagg_client import ZaggConnection
    HOSTNAME = 'use-tower1.ops.rhcloud.com'
    METRICS = [
        'kernel.all',
        'swap.free',
        'swap.length',
        'swap.used',
        ]

    ZAGGCONN = ZaggConnection(host='172.17.0.151', user='admin', password='r3dh@t')

    PCPtoZagg(host=HOSTNAME, zagg_connection=ZAGGCONN, metrics=METRICS).run()
"""

from openshift_tools.monitoring.zagg_client import ZaggClient
from openshift_tools.monitoring import pminfo
from openshift_tools.monitoring.metricmanager import UniqueMetric

class PCPtoZagg(object):
    """
    collect PCP metrics and send them to Zagg
    """

    def __init__(self, host, zagg_connection, metrics=None):
        """
        set up the zagg client, metrics and unique_metrics
        """
        self.zaggclient = ZaggClient(zagg_connection=zagg_connection)
        if isinstance(metrics, basestring):
            metrics = [metrics]
        self.metrics = metrics
        self.host = host
        self.metric_dict = None
        self.unique_metrics = []

    def run(self):
        """
        Go get metrics, convert to UniqueMetric, and send to zagg
        """
        self.get_metrics_from_pminfo()
        self.pm_to_unique_metrics()
        self.send_metrics_to_zagg()

    def get_metrics_from_pminfo(self):
        """
        Evaluate a list of metrics from pcp using pminfo
        """
        self.metric_dict = pminfo.get_metrics(self.metrics)

    def pm_to_unique_metrics(self):
        """
        Convert a dict of metrics into Unique Metrics
        """
        for metric, value in self.metric_dict.iteritems():
            new_unique_metric = UniqueMetric(self.host, metric, value)
            self.unique_metrics.append(new_unique_metric)

    def send_metrics_to_zagg(self):
        """
        Send list of Unique Metrics to Zagg
        """
        self.zaggclient.add_metric(self.unique_metrics)
