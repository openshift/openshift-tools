#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Collect metrics and send metrics to Hawk.  The data
being sent to Hawk is done using REST API using the HawkClient
module

Examples:

    from openshift_tools.monitoring.hawk_common import HawkConnection, HawkHeartbeat
    from openshift_tools.monitoring.hawk_sender import HawkSender
    HOSTNAME = 'host.example.com'

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
from openshift_tools.monitoring.generic_metric_sender import GenericMetricSender

class HawkSender(GenericMetricSender):
    """
    collect and create UniqueMetrics and send them to Hawk
    """

    # Allow for 6 arguments (including 'self')
    # pylint: disable=too-many-arguments
    def __init__(self, host=None, hawk_connection=None, verbose=False, debug=False, config_file=None):
        """
        set up the hawk client and unique_metrics
        """
        super(HawkSender, self).__init__()

        if not config_file:
            config_file = '/etc/openshift_tools/hawk_client.yaml'

        self.config_file = config_file
        self.unique_metrics = []
        self.verbose = verbose
        self.debug = debug

        if not host:
            host = self.get_default_host()

        if not hawk_connection:
            hawk_connection = self._get_default_hawk_connection()

        self.host = host
        self.hawkclient = HawkClient(hawk_connection=hawk_connection)

    def get_default_host(self):
        """ get the 'host' value from the config file """
        self.parse_config()

        return self.config['host']['name']

    def _get_default_hawk_connection(self):
        """ get the values and create a hawk_connection """

        self.parse_config()
        hawk_server = self.config['hawk']['url']
        hawk_user = self.config['hawk']['user']
        hawk_password = self.config['hawk']['pass']
        hawk_ssl_verify = self.config['hawk'].get('ssl_verify', False)
        hawk_debug = self.config['hawk'].get('debug', False)
        hawk_active = self.config['hawk'].get('active', True)

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
                                         active=hawk_active,
                                        )

        return hawk_connection

    def add_metric(self, metrics, host=None, synthetic=False):
        """ create unique metric from key value pair """

        if synthetic and not host:
            host = self.config['synthetic_clusterwide']['host']['name']
        elif not host:
            host = self.host

        hawk_metrics = []

        for key, value in metrics.iteritems():
            hawk_metric = UniqueMetric(host, key, value)
            hawk_metrics.append(hawk_metric)

        self.unique_metrics += hawk_metrics

    def send_metrics(self):
        """
        Send list of Unique Metrics to Hawk
        clear self.unique_metrics
        """
        if self.verbose:
            self.print_unique_metrics_key_value()

        if self.debug:
            self.print_unique_metrics()

        self.hawkclient.push_metrics(self.unique_metrics)
        self.unique_metrics = []
