#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4
"""
HawkClient uses the openshift_tools.web/rest.py

Example usage:

    from openshift_tools.monitoring.metricmanager import UniqueMetric
    from openshift_tools.monitoring.hawk_common import HawkConnection
    from openshift_tools.monitoring.hawk_client import HawkClient

    ml = []
    # UniqueMetric from openshift_tools.monitoring.metricmanager
    new_metric = UniqueMetric('example.com','cpu/usage',12.34)
    ml.append(new_metric)
    new_metric = UniqueMetric('example.org','cpu/usage',4.2)
    ml.append(new_metric)

    # No Auth
    connection = HawkConnection(url='172.17.0.27:8000')

    # Basic Auth
    connection = HawkConnection(url='172.17.0.27:8000', user='user', passwd='password')

    client = HawkClient(connection)
    print client.add_metric(ml)
"""
#These are not installed on the buildbot, disabling this
#pylint: disable=no-name-in-module,unused-import
from openshift_tools.monitoring.metricmanager import UniqueMetric, MetricManager
from openshift_tools.monitoring.hawk_common import HawkConnection

# The hawkular client is optional
try:
    from hawkular.metrics import HawkularMetricsClient, MetricType, Availability
except ImportError:
    pass

#This class implements rest calls. We only have one rest call implemented
# add-metric.  More could be added here
#pylint: disable=too-few-public-methods
class HawkClient(object):
    """
    wrappers class around hawkular client python so use can use it with UniqueMetric
    """

    def __init__(self, hawk_connection, headers=None):
        # pylint doesn't know where RestAPI is
        #pylint: disable=undefined-variable
        self.hawk_conn = hawk_connection
        self.client = None

        # Do not create a client if inactive
        if self.hawk_conn.inactive:
            return

        self.client = HawkularMetricsClient(host=self.hawk_conn.host,
                                            port=self.hawk_conn.port,
                                            scheme=self.hawk_conn.scheme,
                                            username=self.hawk_conn.username,
                                            password=self.hawk_conn.password,
                                            context=self.hawk_conn.context,
                                            tenant_id=self.hawk_conn.tenant_id,
                                           )

    def push_heartbeat(self, metric):
        """
        Push a list of heartbeat metric-endpoints via hawkular client
        """
        # We assume the value of a heartbeat is a dict
        heartbeat = metric.value
        # Hawkular metrics heartbeat value is "up"
        value = Availability.Up
        # Hawkular metrics use milliseconds
        clock = metric.clock * 1000
        # Use MetricType.Availability for heartbeat data
        metric_type = MetricType.Availability

        for template in heartbeat.get('templates'):
            # Add the group and host to the key
            key = '{0}/{1}/{2}'.format('ops/heartbeat', 'template', template)
            self.client.push(metric_type, key, value, clock)

        for hostgroup in heartbeat.get('hostgroups'):
            # Add the group and host to the key
            key = '{0}/{1}/{2}'.format('ops/heartbeat', 'hostgroup', hostgroup)
            self.client.push(metric_type, key, value, clock)

    def add_metric(self, unique_metric_list):
        """
        Add a list of UniqueMetrics (unique_metric_list) via hawkular client
        """
        # Do not run if inactive
        if not self.client:
            return

        metric_list = [m for m in unique_metric_list if m.key != 'heartbeat']
        heartbeat_list = [m for m in unique_metric_list if m.key == 'heartbeat']

        for metric in metric_list:
            # Hawkular metrics support only numeric values
            value = float(metric.value)
            # Hawkular metrics use milliseconds
            clock = metric.clock * 1000
            # Add the group and host to the key
            key = '{0}/{1}/{2}'.format('ops', metric.host, metric.key)
            # Use MetricType.Gauge for metrics data
            metric_type = MetricType.Gauge
            self.client.push(metric_type, key, value, clock)

        for metric in heartbeat_list:
            # Push a list of endpoints for one heartbeat metric
            self.push_heartbeat(metric)

        status, raw_respons = None, None
        return (status, raw_respons)
