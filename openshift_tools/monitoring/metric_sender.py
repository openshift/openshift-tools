#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Wrapper for concrete Metric Sender classes: ZaggSender, HawkSender etc.
Check configuration and send metrics using specific client if enabled.

Examples:

    from openshift_tools.monitoring.metric_sender import MetricSender
    HOSTNAME = 'host.example.com'

    MTSHEARTBEAT = MetricSenderHeartbeat(templates=['template1', 'template2'], hostgroups=['hostgroup1', 'hostgroup2'])

    mts = HawkSender(host=HOSTNAME)
    mts.add_heartbeat(MTSHEARTBEAT)
    mts.add_metric({ 'test.key' : '1' })
    mts.send_metrics()
"""

from collections import namedtuple
from openshift_tools.monitoring.generic_metric_sender import GenericMetricSender
from openshift_tools.monitoring.zagg_sender import ZaggSender
# openshift_tools.monitoring.hawk_sender conditionally imported below

class MetricSender(GenericMetricSender):
    """
    collect and create UniqueMetrics and send them to specific senders
    """

    def __init__(self, host=None, verbose=False, debug=False, config_file=None):
        '''
        Read config file and add specific active senders to sender list
        '''
        super(MetricSender, self).__init__()

        if not config_file:
            config_file = '/etc/openshift_tools/metric_sender.yaml'

        self.config_file = config_file
        self.verbose = verbose
        self.debug = debug
        self.active_senders = list()

        super(MetricSender, self).parse_config()
        if self.is_zagg_active():
            self.active_senders.append(ZaggSender(host=host, verbose=verbose, debug=debug, config_file=config_file))

        if self._is_hawk_active():
            try:
                from openshift_tools.monitoring.hawk_sender import HawkSender
                self.active_senders.append(HawkSender(host=host, verbose=verbose, debug=debug, config_file=config_file))
            except ImportError as err:
                print "ERROR:", err, "(is python-hawkular-client missing?)"
                print "Skipping sending metrics to hawkular."

    def _is_hawk_active(self):
        ''' Check if hawk client is active by configuration'''
        return self.config['hawk'].get('active', True)


    def is_zagg_active(self):
        ''' Check if zagg client is active by configuration'''
        return self.config['zagg'].get('active', True)

    def get_hawk_config_file(self):
        ''' Read hawk sender config file configuration'''
        return self.config['hawk'].get('config_file', None)

    def get_zagg_config_file(self):
        ''' Read zagg sender config file configuration'''
        return self.config['zagg'].get('config_file', None)

    # Allow for 6 arguments (including 'self')
    # pylint: disable=too-many-arguments
    def add_dynamic_metric(self, discovery_key, macro_string, macro_array, host=None, synthetic=False):
        ''' apply add_dynamic_metric for each sender'''
        for sender in self.active_senders:
            sender.add_dynamic_metric(discovery_key, macro_string, macro_array, host, synthetic)

    def add_metric(self, metric, host=None, synthetic=False, key_tags=None):
        ''' apply add_metric for each sender'''
        for sender in self.active_senders:
            sender.add_metric(metric, host, synthetic, key_tags)

    def add_heartbeat(self, heartbeat, host=None):
        ''' apply add_heartbit for each sender'''
        for sender in self.active_senders:
            sender.add_heartbeat(heartbeat, host)

    def send_metrics(self):
        ''' apply send_metrics for each sender'''
        for sender in self.active_senders:
            sender.send_metrics()

    def print_unique_metrics(self):
        """
        This function prints all of the information of the UniqueMetrics that all senders
        currently has stored
        """
        for sender in self.active_senders:
            sender.print_unique_metrics()

MetricSenderHeartbeat = namedtuple("MetricSenderHeartbeat", ["templates", "hostgroups"])
