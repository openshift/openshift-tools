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
import yaml

class OpenshiftKubeconfigChecker(object):
    """ Checks for Openshift Pods """

    def __init__(self):
        self.args = None
        self.zagg_sender = None

    def run(self):
        """  Main function to run the check """

        self.parse_args()
        self.zagg_sender = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)

        status = self.parse_config()

        self.zagg_sender.add_zabbix_keys({
            "openshift.kubeconfig.status" : status})

        self.zagg_sender.send_metrics()

    def parse_config(self):
        """ Load the kubeconfig """

        print "\nAttempt to load the kubeconfig\n"

        try:
            yaml.load(open(self.args.config))
            return 0

        except Exception as ex:
            print "Failed parsing config %s " %ex.message
            return 1


    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Openshift pod sender')
        parser.add_argument('-c', '--config', \
            help='kubeconfig to parse (default /etc/origin/master/admin.kubeconfig)', \
            default='/etc/origin/master/admin.kubeconfig')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

if __name__ == '__main__':
    OSKC = OpenshiftKubeconfigChecker()
    OSKC.run()
