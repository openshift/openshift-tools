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

import argparse
from openshift_tools.web.openshift_rest_api import OpenshiftRestApi
from openshift_tools.monitoring.zagg_sender import ZaggSender


class OpenshiftMasterZaggClient(object):
    """ Checks for the Openshift Master """

    def __init__(self):
        self.args = None
        self.zagg_sender = None
        self.ora = OpenshiftRestApi()

    def run(self):
        """  Main function to run the check """

        self.parse_args()
        self.zagg_sender = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)

        if self.args.healthz or self.args.all_checks:
            self.healthz_check()

        if self.args.project_count or self.args.all_checks:
            self.project_count()

        if self.args.pod_count or self.args.all_checks:
            self.pod_count()

        if self.args.user_count or self.args.all_checks:
            self.user_count()

        self.zagg_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Network metric sender')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        master_check_group = parser.add_argument_group('Different Checks to Perform')
        master_check_group.add_argument('--all-checks', action='store_true', default=None,
                                        help='Do all of the checks')

        master_check_group.add_argument('--healthz', action='store_true', default=None,
                                        help='Query the Openshift Master API /healthz')

        master_check_group.add_argument('--project-count', action='store_true', default=None,
                                        help='Query the Openshift Master for Number of Pods')

        master_check_group.add_argument('--pod-count', action='store_true', default=None,
                                        help='Query the Openshift Master for Number of Running Pods')

        master_check_group.add_argument('--user-count', action='store_true', default=None,
                                        help='Query the Openshift Master for Number of Users')

        self.args = parser.parse_args()

    def healthz_check(self):
        """ check the /healthz API call """

        print "\nPerforming /healthz check..."

        response = self.ora.text_get('/healthz')
        print "healthz check returns: %s " %response

        self.zagg_sender.add_zabbix_keys({'openshift.master.api.healthz' : 'ok' in response})

    def project_count(self):
        """ check the number of projects in Openshift """

        print "\nPerforming project count check..."

        excluded_names = ['openshift', 'openshift-infra', 'default']
        response = self.ora.json_get('/oapi/v1/projects')

        project_names = [project['metadata']['name'] for project in response['items']]
        valid_names = set(project_names) - set(excluded_names)

        print "Project count: %s" % len(valid_names)

        self.zagg_sender.add_zabbix_keys({'openshift.project.counter' : len(valid_names)})

    def pod_count(self):
        """ check the number of pods in Openshift """

        print "\nPerforming pod count check..."

        response = self.ora.json_get('/api/v1/pods')

        running_pod_count = 0
        for i in response['items']:
            if 'containerStatuses' in i['status']:
                if 'running' in i['status']['containerStatuses'][0]['state']:
                    running_pod_count += 1

        print "Total pod count: %s" % len(response['items'])
        print "Running pod count: %s" % running_pod_count

        self.zagg_sender.add_zabbix_keys({'openshift.master.pod.running.count' : running_pod_count,
                                          'openshift.master.pod.total.count' : len(response['items'])})

    def user_count(self):
        """ check the number of users in Openshift """

        print "\nPerforming user count check..."

        response = self.ora.json_get('/oapi/v1/users')

        print "Total user count: %s" % len(response['items'])
        self.zagg_sender.add_zabbix_keys({'openshift.master.user.count' : len(response['items'])})

if __name__ == '__main__':
    OMCZ = OpenshiftMasterZaggClient()
    OMCZ.run()
