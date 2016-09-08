#!/usr/bin/env python
'''
  Send Pod status checks to Zagg
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
# oso modules won't be available to pylint in Jenkins
#pylint: disable=import-error

import argparse
from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.monitoring.hawk_sender import HawkSender
from openshift_tools.web.openshift_rest_api import OpenshiftRestApi
import yaml

class OpenshiftPodChecker(object):
    """ Checks for Openshift Pods """

    def __init__(self):
        self.args = None
        self.ora = None
        self.zagg_sender = None
        self.hawk_sender = None

    def run(self):
        """  Main function to run the check """

        self.parse_args()
        self.ora = OpenshiftRestApi()
        self.zagg_sender = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)
        self.hawk_sender = HawkSender(verbose=self.args.verbose, debug=self.args.debug)

        try:
            self.get_pods()

        except Exception as ex:
            print "Problem retreiving pod data: %s " % ex.message

        self.zagg_sender.send_metrics()
        self.hawk_sender.send_metrics()

    def get_pods(self):
        """ Gets pod data """

        print "\nPerforming pod check ...\n"

        api_url = '/api/v1/pods'
        if (str(self.args.namespace) != "None") & \
            (str(self.args.namespace) != "all"):
            api_url = '/api/v1/namespaces/{}/pods'.format(self.args.namespace)

        api_yaml = self.ora.get(api_url, rtype='text')
        pods = yaml.safe_load(api_yaml)

        pod_count = 0
        for pod in pods["items"]:
            if self.args.pod and \
                self.args.pod in pod["metadata"]["name"]:
                print "status of {} is {}".format(
                    pod["metadata"]["name"],
                    pod["status"]["phase"],
                )
                if pod["status"]["phase"] == "Running":
                    pod_count += 1
            else:
                pass

        self.zagg_sender.add_zabbix_keys(
            {"service.pod.{}.count".format(self.args.pod): pod_count})
        self.hawk_sender.add_zabbix_keys(
            {"service.pod.{}.count".format(self.args.pod): pod_count})


    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Openshift pod sender')
        parser.add_argument('-p', '--pod', default=None, help='Check for pod with this specific name')
        parser.add_argument('-n', '--namespace', default=None, help='Check for pods in this namespace - "all" for all')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

if __name__ == '__main__':
    ODRC = OpenshiftPodChecker()
    ODRC.run()
