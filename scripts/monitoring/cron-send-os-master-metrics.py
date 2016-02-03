#!/usr/bin/env python
'''
  Send Openshift Master stats and metric checks to Zagg
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
# Accepting general Exceptions
#pylint: disable=broad-except
# pylint is flagging this code as being too complex. Refactor it soon! https://trello.com/c/Isne8Dcz
#pylint: disable=too-many-branches

import argparse
import math
from openshift_tools.web.openshift_rest_api import OpenshiftRestApi
from openshift_tools.monitoring.zagg_sender import ZaggSender
from prometheus_client.parser import text_string_to_metric_families

class OpenshiftMasterZaggClient(object):
    """ Checks for the Openshift Master """

    def __init__(self):
        self.args = None
        self.zagg_sender = None
        self.ora = OpenshiftRestApi(verify_ssl=False)

    def run(self):
        """  Main function to run the check """

        self.parse_args()
        self.zagg_sender = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)

        try:
            if self.args.healthz or self.args.all_checks:
                self.healthz_check()

        except Exception as ex:
            print "Problem performing healthz check: %s " % ex.message
            self.zagg_sender.add_zabbix_keys({'openshift.master.api.healthz' : 'false'})

        try:
            if self.args.api_ping or self.args.all_checks:
                self.api_ping()

            if self.args.project_count or self.args.all_checks:
                self.project_count()

            if self.args.pod_count or self.args.all_checks:
                self.pod_count()

            if self.args.user_count or self.args.all_checks:
                self.user_count()

            if self.args.pv_count or self.args.all_checks:
                self.pv_count()

            if self.args.nodes_not_ready or self.args.all_checks:
                self.nodes_not_ready()

        except Exception as ex:
            print "Problem Openshift API checks: %s " % ex.message
            self.zagg_sender.add_zabbix_keys({'openshift.master.api.ping' : 0}) # Openshift API is down

        try:
            if self.args.metrics or self.args.all_checks:
                self.metric_check()

        except Exception as ex:
            print "Problem getting Openshift metrics at /metrics: %s " % ex.message
            self.zagg_sender.add_zabbix_keys({'openshift.master.metric.ping' : 0}) # Openshift Metrics are down

        self.zagg_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Network metric sender')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        master_check_group = parser.add_argument_group('Different Checks to Perform')
        master_check_group.add_argument('--all-checks', action='store_true', default=None,
                                        help='Do all of the checks')

        master_check_group.add_argument('--api-ping', action='store_true', default=None,
                                        help='Verify the Openshift API is alive')

        master_check_group.add_argument('--healthz', action='store_true', default=None,
                                        help='Query the Openshift Master API /healthz')

        master_check_group.add_argument('--metrics', action='store_true', default=None,
                                        help='Query the Openshift Master Metrics at /metrics')

        master_check_group.add_argument('--project-count', action='store_true', default=None,
                                        help='Query the Openshift Master for Number of Pods')

        master_check_group.add_argument('--pod-count', action='store_true', default=None,
                                        help='Query the Openshift Master for Number of Running Pods')

        master_check_group.add_argument('--user-count', action='store_true', default=None,
                                        help='Query the Openshift Master for Number of Users')

        master_check_group.add_argument('--pv-count', action='store_true', default=None,
                                        help='Query the Openshift Master for number of Persistent Volumes')

        master_check_group.add_argument('--nodes-not-ready', action='store_true', default=None,
                                        help='Query the Openshift Master for number of nodes not in Ready state')

        self.args = parser.parse_args()

    def api_ping(self):
        """ Verify the Openshift API health is responding correctly """

        print "\nPerforming Openshift API ping check..."

        response = self.ora.get('/api/v1/nodes')
        print "\nOpenshift API ping is alive"
        print "Number of nodes in the Openshift cluster: %s" % len(response['items'])

        self.zagg_sender.add_zabbix_keys({'openshift.master.api.ping' : 1,
                                          'openshift.master.node.count': len(response['items'])})

    def healthz_check(self):
        """ check the /healthz API call """

        print "\nPerforming /healthz check..."

        response = self.ora.get('/healthz', rtype='text')
        print "healthz check returns: %s " %response

        self.zagg_sender.add_zabbix_keys({'openshift.master.api.healthz' : str('ok' in response).lower()})

    def metric_check(self):
        """ collect certain metrics from the /metrics API call """

        print "\nPerforming /metrics check..."
        response = self.ora.get('/metrics', rtype='text')

        for metric_type in text_string_to_metric_families(response):

            # Collect the apiserver_request_latencies_summary{resource="pods",verb="LIST",quantiles in /metrics
            # Collect the apiserver_request_latencies_summary{resource="pods",verb="WATCHLIST",quantiles in /metrics
            if metric_type.name == 'apiserver_request_latencies_summary':
                key_str = 'openshift.master.apiserver.latency.summary'
                for sample in metric_type.samples:
                    if (sample[1]['resource'] == 'pods'
                            and sample[1].has_key('quantile')
                            and 'LIST' in sample[1]['verb']):
                        curr_key_str = key_str + ".pods.quantile.%s.%s" % (sample[1]['verb'],
                                                                           sample[1]['quantile'].split('.')[1])

                        if math.isnan(sample[2]):
                            value = 0
                        else:
                            value = sample[2]

                        self.zagg_sender.add_zabbix_keys({curr_key_str.lower(): int(value/1000)})

            # Collect the scheduler_e2e_scheduling_latency_microseconds{quantiles in /metrics
            if metric_type.name == 'scheduler_e2e_scheduling_latency_microseconds':
                for sample in metric_type.samples:
                    if sample[1].has_key('quantile'):
                        key_str = 'openshift.master.scheduler.e2e.scheduling.latency'
                        curr_key_str = key_str + ".quantile.%s" % (sample[1]['quantile'].split('.')[1])

                        if math.isnan(sample[2]):
                            value = 0
                        else:
                            value = sample[2]

                        self.zagg_sender.add_zabbix_keys({curr_key_str.lower(): int(value/1000)})

        self.zagg_sender.add_zabbix_keys({'openshift.master.metric.ping' : 1}) #

    def project_count(self):
        """ check the number of projects in Openshift """

        print "\nPerforming project count check..."

        excluded_names = ['openshift', 'openshift-infra', 'default', 'ops-monitor']
        response = self.ora.get('/oapi/v1/projects')

        project_names = [project['metadata']['name'] for project in response['items']]
        valid_names = set(project_names) - set(excluded_names)

        print "Project count: %s" % len(valid_names)

        self.zagg_sender.add_zabbix_keys({'openshift.project.count' : len(valid_names)})

    def pod_count(self):
        """ check the number of pods in Openshift """

        print "\nPerforming pod count check..."

        response = self.ora.get('/api/v1/pods')

        # Get running pod count
        running_pod_count = 0
        for i in response['items']:
            if 'containerStatuses' in i['status']:
                if 'running' in i['status']['containerStatuses'][0]['state']:
                    running_pod_count += 1

        # Get running pod count on compute only nodes (non-infra)
        running_user_pod_count = 0
        for i in response['items']:
            if 'containerStatuses' in i['status']:
                if 'running' in i['status']['containerStatuses'][0]['state']:
                    if 'nodeSelector' in i['spec']:
                        if i['spec']['nodeSelector']['type'] == 'compute':
                            running_user_pod_count += 1


        print "Total pod count: %s" % len(response['items'])
        print "Running pod count: %s" % running_pod_count
        print "User Running pod count: %s" % running_user_pod_count

        self.zagg_sender.add_zabbix_keys({'openshift.master.pod.running.count' : running_pod_count,
                                          'openshift.master.pod.user.running.count' : running_user_pod_count,
                                          'openshift.master.pod.total.count' : len(response['items'])})

    def user_count(self):
        """ check the number of users in Openshift """

        print "\nPerforming user count check..."

        response = self.ora.get('/oapi/v1/users')

        print "Total user count: %s" % len(response['items'])
        self.zagg_sender.add_zabbix_keys({'openshift.master.user.count' : len(response['items'])})

    def pv_count(self):
        """ check the number of persistent volumes in Openshift """

        print "\nPerforming user persistent volume count...\n"

        response = self.ora.get('/api/v1/persistentvolumes')
        pv_types = {'Available': 0,
                    'Bound': 0,
                    'Released': 0,
                    'Failed': 0}

        for item in response['items']:
            pv_types[item['status']['phase']] += 1

        print "Total Persistent Volume Total count: %s" % len(response['items'])
        self.zagg_sender.add_zabbix_keys(
            {'openshift.master.pv.total.count' : len(response['items'])})

        for key, value in pv_types.iteritems():
            print "Total Persistent Volume %s count: %s" % (key, value)
            self.zagg_sender.add_zabbix_keys(
                {'openshift.master.pv.%s.count' %key.lower() : value})

    def nodes_not_ready(self):
        """ check the number of nodes in the cluster that are not ready"""

        print "\nPerforming nodes not ready check..."

        response = self.ora.get('/api/v1/nodes')

        nodes_not_schedulable = []

        for n in response['items']:
            if "unschedulable" in n['spec']:
                nodes_not_schedulable.append(n)

        nodes_not_ready = []

        for n in response['items']:
            if n['status']['conditions'][0]['reason'] != "KubeletReady":
                nodes_not_ready.append(n)

        print "Count of nodes not schedulable: %s" % len(nodes_not_schedulable)
        print "Count of nodes not ready: %s" % len(nodes_not_ready)

        self.zagg_sender.add_zabbix_keys(
            {'openshift.master.nodesnotready.count' : len(nodes_not_ready)})

        self.zagg_sender.add_zabbix_keys(
            {'openshift.master.nodesnotschedulable.count' : len(nodes_not_schedulable)})

if __name__ == '__main__':
    OMCZ = OpenshiftMasterZaggClient()
    OMCZ.run()
