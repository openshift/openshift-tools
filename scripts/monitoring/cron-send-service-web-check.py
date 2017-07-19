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
import urllib2
import socket
import yaml
from openshift_tools.monitoring.metric_sender import MetricSender
from openshift_tools.web.openshift_rest_api import OpenshiftRestApi

class OpenshiftWebServiceChecker(object):
    """ Checks for Openshift Pods """

    def __init__(self):
        self.args = None
        self.ora = None
        self.metric_sender = None
        self.service_ip = None
        self.service_port = '443'
        self.servicecount = 0

    def run(self):
        """  Main function to run the check """

        self.parse_args()
        self.ora = OpenshiftRestApi()
        self.metric_sender = MetricSender(verbose=self.args.verbose, debug=self.args.debug)

        status = None
        try:
            self.get_service()
            if not self.args.service_count:
                status = self.check_service()

        except Exception as ex:
            print "Problem retreiving data: %s " % ex.message

        if status:
            self.metric_sender.add_metric({
                "openshift.webservice.{}.status".format(self.args.pod) : status})

        self.metric_sender.add_metric({'openshift.cluster.service.count': self.servicecount}, synthetic=True)
        self.metric_sender.send_metrics()

    def get_service(self):
        """ Gets the service for a pod """

        print "\nLooking up services for pod\n"

        api_url = "/api/v1/services"
        if (str(self.args.namespace) != "None") & \
            (str(self.args.namespace) != "all"):
            api_url = '/api/v1/namespaces/{}/services'.format(self.args.namespace)

        print "using api url {}".format(api_url)

        api_yaml = self.ora.get(api_url, rtype='text')
        services = yaml.safe_load(api_yaml)

        self.servicecount = len(services['items'])
        for service in services["items"]:
            if self.args.pod and \
                self.args.pod in service["metadata"]["name"]:
                print "service IP is {}".format(service["spec"]["clusterIP"])
                self.service_ip = service["spec"]["clusterIP"]
                if self.args.portname != None:
                    for port in service["spec"]["ports"]:
                        if port["name"] == self.args.portname:
                            self.service_port = port["port"]
                else:
                    self.service_port = service["spec"]["ports"][0]["port"]
            else:
                pass

    def check_service(self):
        """ Checks the web service """

        print "\nChecking web service\n"

        if self.args.insecure:
            proto = 'http'
        else:
            proto = 'https'

        url = '{}://{}:{}/{}'.format(
            proto,
            self.service_ip,
            self.service_port,
            self.args.url,
        )

        try:
            print "Performing check on URL: {}".format(url)
            response = urllib2.urlopen(url, timeout=30)

            if str(response.getcode()) == self.args.status:
                if self.args.content is None \
                    or self.args.content in response.read():
                    return True

        except urllib2.URLError:
            print "Received error accessing URL: {}".format(url)
        except socket.timeout:
            print "Timed out accessing URL: {}".format(url)

        return False


    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Openshift pod sender')
        parser.add_argument('-p', '--pod', default=None, help='Check for pod with this specific name')
        parser.add_argument('-n', '--namespace', default=None, help='Check for pods in this namespace - "all" for all')
        parser.add_argument('-P', '--portname', default=None, help='name of the port to check')
        parser.add_argument('-u', '--url', default="/", help='URL to check. Defaults to "/".')
        parser.add_argument('-s', '--status', default="200", help='HTTP status code to expect. Defaults to 200')
        parser.add_argument('-c', '--content', default=None, help='Looks for a string in the content of the response.')
        parser.add_argument('-i', '--insecure', help='Use insecure http connection')
        parser.add_argument('-S', '--secure', help='Use secure https connection (default)')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('-x', '--service-count', action='store_true', default=0,
                            help='Find the total count of services')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

if __name__ == '__main__':
    OWSC = OpenshiftWebServiceChecker()
    OWSC.run()
