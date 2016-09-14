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
#pylint: disable=no-name-in-module,unused-import,import-error
from openshift_tools.monitoring.metricmanager import UniqueMetric, MetricManager
from openshift_tools.monitoring.hawk_common import HawkConnection

# The hawkular client
from hawkular.metrics import HawkularMetricsClient, MetricType, Availability

#This class implements rest calls. We only have one rest call implemented
# add-metric.  More could be added here
#pylint: disable=too-few-public-methods
class HawkClient(object):
    """
    wrappers class around hawkular client python so use can use it with UniqueMetric
    """

    def __init__(self, hawk_connection):
        # pylint doesn't know where RestAPI is
        #pylint: disable=undefined-variable
        self.hawk_conn = hawk_connection
        self.client = None

        # Do not create a client if inactive
        if not self.hawk_conn.active:
            return

        self.client = HawkularMetricsClient(host=self.hawk_conn.host,
                                            port=self.hawk_conn.port,
                                            scheme=self.hawk_conn.scheme,
                                            username=self.hawk_conn.username,
                                            password=self.hawk_conn.password,
                                            context=self.hawk_conn.context,
                                            tenant_id=self.hawk_conn.tenant_id,
                                           )

    def add_metric(self, unique_metric_list):
        """
        Add a list of UniqueMetrics (unique_metric_list) via hawkular client
        """
        # Do not run if inactive
        if not self.hawk_conn.active:
            return

        # We do not support zabbix heartbeat in hawkular
        metric_list = [m for m in unique_metric_list if m.key != 'heartbeat']

        for metric in metric_list:
            # Hawkular metrics support any numeric values
            value = metric.value
            # Hawkular metrics use milliseconds
            clock = metric.clock * 1000
            # Add the type and host to the key, this is needed because in hawkular,
            # these need to be namespaced otherwise multiple hosts will be adding
            # values to the same key. See common metrics keys proposal.
            _type = 'node'
            _id = metric.host
            key = '{0}/{1}/{2}'.format(_type, _id, metric.key)
            # Use MetricType.Gauge for numeric metrics data
            metric_type = MetricType.Gauge
            self.client.push(metric_type, key, value, clock)

        status, raw_respons = None, None
        return (status, raw_respons)
