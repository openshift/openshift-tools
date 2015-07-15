#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4
"""
ZaggClient uses the openshift_tools.web/rest.py

Example usage:


    from openshift_tools.monitoring.zagg_common import ZaggConnection

     ml = []
     # UniqueMetric from openshift_tools.monitoring.metricmanager
     new_metric = UniqueMetric('a','b','c')
     ml.append(new_metric)
     new_metric = UniqueMetric('d','e','f')
     ml.append(new_metric)

     # No Auth
     zc = ZaggClient(host='172.17.0.27:8000')

     # Basic Auth
     zc = ZaggClient(host='172.17.0.27:8000', user='user', passwd='password')

     print zc.add_metric(ml)

"""
#These are not installed on the buildbot, disabling this
#pylint: disable=no-name-in-module,unused-import
from openshift_tools.monitoring.metricmanager import UniqueMetric, MetricManager
from openshift_tools.monitoring.zagg_common import ZaggConnection
from openshift_tools.web.rest import RestApi
import json

#This class implements rest calls. We only have one rest call implemented
# add-metric.  More could be added here
#pylint: disable=too-few-public-methods
class ZaggClient(object):
    """
    wrappers class around REST API so use can use it with python
    """

    def __init__(self, zagg_connection, headers=None):
        # pylint doesn't know where RestAPI is
        #pylint: disable=undefined-variable
        self.zagg_conn = zagg_connection
        self.rest = RestApi(host=self.zagg_conn.host,
                            username=self.zagg_conn.user,
                            password=self.zagg_conn.password,
                            headers=headers
                           )

    def add_metric(self, unique_metric_list):
        """
        Add a list of UniqueMetrics (unique_metric_list) via rest
        """
        metric_list = []
        for metric in unique_metric_list:
            metric_list.append(metric.to_dict())

        headers = {'content-type': 'application/json; charset=utf8'}
        status, raw_response = self.rest.request(method='POST', url='metric',
                                                 data=json.dumps(unique_metric_list, default=lambda x: x.__dict__),
                                                 headers=headers)

        return (status, raw_response)
