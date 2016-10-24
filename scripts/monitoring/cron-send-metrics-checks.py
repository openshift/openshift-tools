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

import ssl
import yaml
import urllib2
import argparse

# pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.zagg_sender import ZaggSender
# pylint: enable=import-error

# These are here for a metrics pre 3.4 workaround
import sys
import tempfile
import shutil
import base64

class OpenshiftMetricsStatus(object):
    '''
        This is a check for making sure metrics is up and running
        and nodes fluentd can populate data from each node
    '''
    def __init__(self):
        ''' Initializze OpoenShiftMetricsStatus class '''
        self.kubeconfig = '/tmp/admin.kubeconfig'
        self.zagg_sender = None
        self.oc = None
        self.args = None
        self.deployer_pod_name = None
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
                pod_report[pod_pretty_name]['starttime'] = int(pod_start_time.strftime("%s"))
                # pylint: enable=E1101

        return pod_report

    def check_node_metrics(self):
        ''' Verify that fluentd on all nodes is able to talk to and populate data in hawkular '''
        # Check to see if secret for htpasswd exists
        try:
            # If so get http password from secret
            secret = self.oc.get_secrets("hawkular-htpasswd")
            self.hawkular_username = base64.b64decode(secret['data']['hawkular-username'])
            self.hawkular_password = base64.b64decode(secret['data']['hawkular-password'])
        except:
            # If not create secret wiith http password
            # This is VERY expensive.
            # So we want to make sure we only run it ONCE per cluster
            deployer_log = self.oc.get_log(self.deployer_pod_name)
            for line in deployer_log.split('\n'):
                if "hawkular_metrics_password" in line:
                    self.hawkular_username = 'hawkular'
                    self.hawkular_password = line.split('=')[-1]

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
        hawkular_url_end = ",type:node,group_id:/memory/usage&buckets=1&start=-1mn"

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
                result = yaml.load(resp.read())
                if result[0]['empty']:
                    return 0

            except urllib2.URLError:
                return 0

        return 1

    def report_to_zabbix(self, pods_status, node_health):
        ''' Report all of our findings to zabbix '''
        discovery_key_metrics = 'openshift.metrics.hawkular'
        item_prototype_macro_metrics = '#OSO_METRICS'
        item_prototype_key_status = 'openshift.metrics.hawkular.status'
        item_prototype_key_starttime = 'openshift.metrics.hawkular.starttime'
        item_prototype_key_restarts = 'openshift.metrics.hawkular.restarts'

        self.zagg_sender.add_zabbix_dynamic_item(discovery_key_metrics,
                                                 item_prototype_macro_metrics,
                                                 pods_status.keys())

        for pod, data in pods_status.iteritems():
            if self.args.verbose:
                for key, val in data.items():
                    print
                    print "%s: Key[%s] Value[%s]" % (pod, key, val)

            self.zagg_sender.add_zabbix_keys({
                "%s[%s]" %(item_prototype_key_status, pod) : data['status'],
                "%s[%s]" %(item_prototype_key_starttime, pod) : data['starttime'],
                "%s[%s]" %(item_prototype_key_restarts, pod) : data['restarts']})

        self.zagg_sender.add_zabbix_keys({'openshift.metrics.nodes_reporting': node_health})
        self.zagg_sender.send_metrics()

    def run(self):
        ''' Main function that runs the check '''
        self.parse_args()
        self.zagg_sender = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)

        self.oc = OCUtil(namespace='openshift-infra', config_file=self.kubeconfig, verbose=self.args.verbose)

        pod_report = self.check_pods()
        metrics_report = self.check_node_metrics()

        self.report_to_zabbix(pod_report, metrics_report)

if __name__ == '__main__':
    OSMS = OpenshiftMetricsStatus()
    OSMS.run()
