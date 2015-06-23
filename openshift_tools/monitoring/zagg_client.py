#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4
"""
REST API for Zagg

Example usage:

     ml = []
     # UniqueMetric from openshift_tools.monitoring.metricmanager
     new_metric = UniqueMetric('a','b','c')
     ml.append(new_metric)
     new_metric = UniqueMetric('d','e','f')
     ml.append(new_metric)

     mr = ZaggClient(host='172.17.0.27:8000')
     print mr.add_metric(ml)

"""
#These are not installed on the buildbot, disabling this
#pylint: disable=no-name-in-module,unused-import
from openshift_tools.web.rest import RestAPI
from openshift_tools.monitoring.metricmanager import UniqueMetric, MetricManager
import json

#This class implements rest calls. We only have one rest call implemented
# add-metric.  More could be added here
#pylint: disable=too-few-public-methods
class ZaggClient(object):
    """
    wrappers class around REST API so use can use it with python
    """
    rest = None
    user = None
    passwd = None

    def __init__(self, host, user=None, passwd=None, headers=None):

        # pylint doesn't know where RestAPI is
        #pylint: disable=undefined-variable
        self.rest = RestApi(host=host, username=user, password=passwd, headers=headers)

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

# This is for testing
#if __name__ == "__main__":
#
#    ml = []
#    new_metric = UniqueMetric('a','b','c')
#    ml.append(new_metric)
#    new_metric = UniqueMetric('d','e','f')
#    ml.append(new_metric)
#
#    mr = MetricRest(host='172.17.0.27:8000')
#    print mr.add_metric(ml)
