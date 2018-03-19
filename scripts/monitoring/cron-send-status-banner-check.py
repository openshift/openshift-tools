import json
import urllib2
import os
import argparse
import logging
from openshift_tools.monitoring.metric_sender import MetricSender

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
commandDelay = 5
local_report_details_dir = '/opt/failure_reports/'
max_details_report_files = 5


class OpenshiftStatusBanner(object):
    def __init__(self):
        ''' Initialize OpenShiftMetricsStatus class '''
        self.metric_sender = None
        self.oc = None
        self.args = None
        self.pageid = None
        self.authid = None

    def parse_args(self):
        ''' Parse arguments passed to the script '''
        parser = argparse.ArgumentParser(description='OpenShift Cluster Unresovled Banner Checker')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose output')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

    def report_to_zabbix(self, data):
        '''send data to zabbix'''
        discovery_key_metrics = 'openshift.status.unresolved.banner'
        item_prototype_macro_metrics = '#OSO_BANNER'
        for each_incident in data:
            components = each_incident['components']
            # get all the groups related with the incident , eg: tsi
            groupids = []
            for component in components:
                groupids.append(component['group_id'])

            group_name = self.query_comonents(groupids[0])
            logger.info("one banner related with %s" % group_name)

            self.metric_sender.add_dynamic_metric(discovery_key_metrics,
                                                  item_prototype_macro_metrics,
                                                  group_name)
            self.metric_sender.add_metric({"openshift.status.unresolved.banner[%s]" % group_name: '1'})

        self.metric_sender.send_metrics()

    def query_banner_info(self):
        '''query status for unresovled banner'''

        url = "https://api.statuspage.io/v1/pages/" + self.pageid + "/incidents/unresolved.json"

        request = urllib2.Request(url)

        request.add_header("Authorization", "OAuth %s" % self.authid)

        try:

            result = urllib2.urlopen(request)

            result_d = result.read()

            data = json.loads(result_d)

        except Exception as e:
            logger.exception("something wrong when trying get the banner info")
            raise e

        return data

    def query_comonents(self, groupid):
        '''query status for component name '''

        group_name = None

        url = "https://api.statuspage.io/v1/pages/" + self.pageid + "/components.json"

        request = urllib2.Request(url)

        request.add_header("Authorization", "OAuth %s" % self.authid)

        try:

            result = urllib2.urlopen(request)

            result_d = result.read()

            data = json.loads(result_d)

            # do the loop to check the component name
            for component in data:
                if component['id'] == groupid:
                    group_name = component['name']


        except Exception as e :
            logger.exception("something wrong when trying to get component")
            raise e

        return group_name

    def checkbanner(self):
        self.parse_args()
        self.metric_sender = MetricSender(verbose=self.args.verbose, debug=self.args.debug)

        self.pageid = os.environ['pageid']
        self.authid = os.environ['authid']

        data = self.query_banner_info()
        if data:
            logger.info("we current have %s unrelved banner" % len(data))
            self.report_to_zabbix(data)
        else:
            logger.error('something wrong')


if __name__ == '__main__':
    BANNER = OpenshiftStatusBanner()
    BANNER.checkbanner()

