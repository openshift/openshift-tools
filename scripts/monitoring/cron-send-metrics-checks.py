#!/usr/bin/env python
'''
  Send Cluster Metrics checks to Zagg
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#
#   Copyright 2015 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
#If a check throws an exception it is failed and should alert
#pylint: disable=bare-except
#pylint: disable=wrong-import-position
#pylint: disable=line-too-long
import ssl
import urllib2
import argparse
import time

# These are here for a metrics pre 3.4 workaround
import sys
import tempfile
import shutil
import base64


import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
commandDelay = 5

import yaml

# pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender
# pylint: enable=import-error

class OpenshiftMetricsStatus(object):
    '''
        This is a check for making sure metrics is up and running
        and nodes fluentd can populate data from each node
    '''
    def __init__(self):
        ''' Initialize OpenShiftMetricsStatus class '''
        self.metric_sender = None
        self.oc = None
        self.args = None
        self.deployer_pod_name = None
        self.hawkular_pod_name = None
        self.hawkular_username = None
        self.hawkular_password = None

    def parse_args(self):
        ''' Parse arguments passed to the script '''
        parser = argparse.ArgumentParser(description='OpenShift Cluster Metrics Checker')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose output')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

    def check_pods(self):
        ''' Check all metrics related pods '''
        pods = self.oc.get_pods()
        pod_report = {}

        for pod in pods['items']:
            if 'metrics-infra' in pod['metadata']['labels']:
                pod_name = pod['metadata']['name']

                # We do not care to monitor the deployer pod
                if pod_name.startswith('metrics-deployer'):
                    self.deployer_pod_name = pod_name
                    continue

                if pod_name.startswith('hawkular-metrics-'):
                    self.hawkular_pod_name = pod_name

                pod_pretty_name = pod['metadata']['labels']['name']
                pod_report[pod_pretty_name] = {}

                # Get the pods ready status
                pod_report[pod_pretty_name]['status'] = int(pod['status']['containerStatuses'][0]['ready'])

                # Number of times a pod has been restarted
                pod_report[pod_pretty_name]['restarts'] = pod['status']['containerStatuses'][0]['restartCount']

                # Get the time the pod was started, otherwise return 0
                if 'state' in pod['status']['containerStatuses'][0]:
                    if 'running' in pod['status']['containerStatuses'][0]['state']:
                        if 'startedAt' in pod['status']['containerStatuses'][0]['state']['running']:
                            pod_start_time = pod['status']['containerStatuses'][0]['state']['running']['startedAt']
                else:
                    pod_start_time = 0

                # Since we convert to seconds it is an INT but pylint still complains. Only disable here
                # pylint: disable=E1101
                # pylint: disable=maybe-no-member
                pod_report[pod_pretty_name]['starttime'] = int(pod_start_time.strftime("%s"))
                # pylint: enable=E1101
                # pylint: enable=maybe-no-member

        return pod_report

    def get_hawkular_creds(self):
        '''
            Looks up hawkular username and password in a secret.
            If the secret does not exist parse it out of the deploy log.
        '''
        # Check to see if secret for htpasswd exists
        try:
            # If so get http password from secret
            secret = self.oc.get_secrets("hawkular-htpasswd")
            # We have seen cases where username and passwork have gotten an added newline to the end
            self.hawkular_username = base64.b64decode(secret['data']['hawkular-username']).rstrip('\n')
            self.hawkular_password = base64.b64decode(secret['data']['hawkular-password']).rstrip('\n')
        except:
            passwd_file = "/client-secrets/hawkular-metrics.password"
            self.hawkular_username = 'hawkular'
            self.hawkular_password = self.oc.run_user_cmd("rsh {} cat {}".format(self.hawkular_pod_name, passwd_file))
            self.hawkular_password = self.hawkular_password.rstrip('\n')

            new_secret = {}
            new_secret['username'] = self.hawkular_username
            new_secret['password'] = self.hawkular_password

            directory_name = tempfile.mkdtemp()
            file_loc = "{}/hawkular-username".format(directory_name)
            temp_file = open(file_loc, 'a')
            temp_file.write(self.hawkular_username)
            temp_file.close()

            file_loc = "{}/hawkular-password".format(directory_name)
            temp_file = open(file_loc, 'a')
            temp_file.write(self.hawkular_password)
            temp_file.close()

            self.oc.run_user_cmd("secrets new hawkular-htpasswd {}".format(directory_name))
            shutil.rmtree(directory_name)

        if not self.hawkular_username or not self.hawkular_password:
            print "Failed to get hawkular username or password"
            sys.exit(1)

    def check_node_metrics(self):
        ''' Verify that fluentd on all nodes is able to talk to and populate data in hawkular '''
        # Get all nodes
        nodes = self.oc.get_nodes()
        # Get the hawkular route
        route = self.oc.get_route('hawkular-metrics')['status']['ingress'][0]['host']

        # Setup the URL headers
        auth_header = "Basic {}".format(
            base64.b64encode("{}:{}".format(self.hawkular_username, self.hawkular_password))
        )
        headers = {"Authorization": "{}".format(auth_header),
                   "Hawkular-tenant": "_system"}

        # Build url
        hawkular_url_start = "https://{}/hawkular/metrics/gauges/data?tags=nodename:".format(route)
        hawkular_url_end = ",type:node,group_id:/memory/usage&buckets=1&start=-2mn&end=-1mn"

        result = 1
        # Loop through nodes
        for item in nodes['items']:
            hawkular_url = "{}{}{}".format(hawkular_url_start, item['metadata']['name'], hawkular_url_end)

            # Disable SSL to work around self signed clusters
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            # Call hawkular for the current node
            try:
                request = urllib2.Request(hawkular_url, headers=headers)
                resp = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx)).open(request)
                res = yaml.load(resp.read())
                if res[0]['empty']:
                    if self.args.verbose:
                        print "WARN - Node not reporting metrics: %s" % item['metadata']['name']
                    result = 0

            except urllib2.URLError as e:
                if self.args.verbose:
                    print "ERROR - Failed to query hawkular - %s" % e
                result = 0

        return result

    def report_to_zabbix(self, pods_status, node_health):
        ''' Report all of our findings to zabbix '''
        discovery_key_metrics = 'openshift.metrics.hawkular'
        item_prototype_macro_metrics = '#OSO_METRICS'
        item_prototype_key_status = 'openshift.metrics.hawkular.status'
        item_prototype_key_starttime = 'openshift.metrics.hawkular.starttime'
        item_prototype_key_restarts = 'openshift.metrics.hawkular.restarts'

        self.metric_sender.add_dynamic_metric(discovery_key_metrics,
                                              item_prototype_macro_metrics,
                                              pods_status.keys())

        for pod, data in pods_status.iteritems():
            if self.args.verbose:
                for key, val in data.items():
                    print
                    print "%s: Key[%s] Value[%s]" % (pod, key, val)

            self.metric_sender.add_metric({
                "%s[%s]" %(item_prototype_key_status, pod) : data['status'],
                "%s[%s]" %(item_prototype_key_starttime, pod) : data['starttime'],
                "%s[%s]" %(item_prototype_key_restarts, pod) : data['restarts']})

        self.metric_sender.add_metric({'openshift.metrics.nodes_reporting': node_health})
        self.metric_sender.send_metrics()

    def run(self):
        ''' Main function that runs the check '''
        self.parse_args()
        self.metric_sender = MetricSender(verbose=self.args.verbose, debug=self.args.debug)

        self.oc = OCUtil(namespace='openshift-infra', config_file='/tmp/admin.kubeconfig', verbose=self.args.verbose)

        pod_report = self.check_pods()
        self.get_hawkular_creds()
        metrics_report = self.check_node_metrics()
        # if metrics_report = 0, we need this check run again
        if metrics_report == 0:
            # sleep for 5 seconds, then run the second time node check
            logger.info("The first time metrics check failed, 5 seconds later will start a second time check")
            time.sleep(commandDelay)
            logger.info("starting the second time metrics check")
            metrics_report = self.check_node_metrics()

        self.report_to_zabbix(pod_report, metrics_report)

if __name__ == '__main__':
    OSMS = OpenshiftMetricsStatus()
    OSMS.run()
