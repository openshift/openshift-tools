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
import os
from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.web.openshift_rest_api import OpenshiftRestApi
import yaml
import urllib2
import socket

class OpenshiftWebServiceChecker(object):
    """ Checks for Openshift Pods """

    def __init__(self):
        self.args = None
        self.ora = None
        self.zagg_sender = None
        self.service_ip = None
        self.service_port = '443'

    def run(self):
        """  Main function to run the check """

        self.parse_args()
        self.ora = OpenshiftRestApi()
        self.zagg_sender = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)

        try:
            self.get_service()
            status = self.check_service()

        except Exception as ex:
            print "Problem retreiving data: %s " % ex.message
        
        self.zagg_sender.add_zabbix_keys({
            "openshift.webservice.{}.status".format(self.args.pod) : status})

        self.zagg_sender.send_metrics()

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

        for service in services["items"]:
            if self.args.pod and \
                self.args.pod in service["metadata"]["name"]:
                print "service IP is {}".format(service["spec"]["clusterIP"])
                self.service_ip = service["spec"]["clusterIP"]
                if self.args.portname != None:
                    for port in service["spec"]["ports"]:
                        if port["name"] == self.arg.portname:
                            self.service_port = port["port"]
                else: 
                    self.service_port=service["spec"]["ports"][0]["port"]
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
                if self.args.content == None \ 
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
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

if __name__ == '__main__':
    OWSC = OpenshiftWebServiceChecker()
    OWSC.run()
