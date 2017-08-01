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

    HAWKCONN = HawkConnection(url='https://172.17.0.151', user='admin', password='pass')

    hs = HawkSender(host=HOSTNAME, hawk_connection=HAWKCONN)
    hs.add_metric({ 'test.key' : '1' })
    hs.send_metrics()
"""
import re
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
            config_file = '/etc/openshift_tools/metric_sender.yaml'

        self.config_file = config_file
        self.unique_metrics = []
        self.verbose = verbose
        self.debug = debug
        self.dynamic_tag_rules = []

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

    @staticmethod
    def update_tags_for_key(key, metric_tags, rules):
        ''' check rules and add tags that match this key '''

        for rule in rules:
            compiled_rule = re.compile(rule.get('regex'))
            if compiled_rule.match(key):
                metric_tags.update(rule.get('tags') or {})

    def add_metric(self, metrics, host=None, synthetic=False, key_tags=None):
        """ create unique metric from key value pair """

        if not key_tags:
            key_tags = {}

        if synthetic and not host:
            host = self.config['synthetic_clusterwide']['host']['name']
        elif not host:
            host = self.host

        hawk_metrics = []

        config_rules = self.config.get('metadata_rules') or []

        metric_tags = {}

        for key, value in metrics.iteritems():
            self.update_tags_for_key(key, metric_tags, config_rules)

            #override configuration with dynamic tags
            self.update_tags_for_key(key, metric_tags, self.dynamic_tag_rules)

            #override configuration with runtime parameters
            metric_tags.update(key_tags)
            hawk_metric = UniqueMetric(host, key, value, tags=metric_tags)
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


    def add_dynamic_metric(self, discovery_key, macro_string, macro_array, host=None, synthetic=False):
        """
        Create regular expressions adding tag - macro_string - to each key in macro_array.
        discovery key is the key prefix
        """

        for macro in macro_array:
            regex = r'%s.*\[%s\]' % (discovery_key, macro)
            # strip "#" from macro string (zabbix specific formatting. irrelevant to hawk
            tag = macro_string[1:] if macro_string.startswith("#") else macro_string
            rule = {'regex': regex, 'tags': {tag: macro}}
            self.dynamic_tag_rules.append(rule)
