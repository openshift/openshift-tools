#!/usr/bin/env python
'''
  Send Cluster Docker Registry checks to Zagg
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
from openshift_tools.monitoring.ocutil import OCUtil
import requests
import urllib2
import yaml

class OpenshiftDockerRegigtryChecker(object):
    """ Checks for the Openshift Cluster Docker Registry """

    def __init__(self):
        self.args = None
        self.zagg_sender = None

        self.docker_hosts = []
        self.docker_port = None
        self.docker_protocol = 'https'

    def get_kubeconfig(self):
        ''' Find kubeconfig to use for OCUtil '''
        # Default master kubeconfig
        kubeconfig = '/etc/origin/master/admin.kubeconfig'
        non_master_kube_dir = '/etc/origin/node'

        if os.path.isdir(non_master_kube_dir):
            for my_file in os.listdir(non_master_kube_dir):
                if my_file.endswith(".kubeconfig"):
                    kubeconfig = os.path.join(non_master_kube_dir, my_file)

        if self.args.debug:
            print "Using kubeconfig: {}".format(kubeconfig)

        self.kubeconfig = kubeconfig

    def run(self):
        """  Main function to run the check """

        self.parse_args()
        self.get_kubeconfig()
        ocutil = OCUtil(config_file=self.kubeconfig, verbose=self.args.verbose)
        self.zagg_sender = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)

        try:
            oc_yaml = ocutil.get_endpoint('docker-registry')
            self.get_registry_service(oc_yaml)
        except Exception as ex:
            print "Problem retreiving registry IPs: %s " % ex.message
            self.zagg_sender.add_zabbix_keys({'openshift.master.registry.healthy_pct' : 0})

        self.registry_health_check()

        self.zagg_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Openshift Cluster Docker Registry sender')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

    def get_registry_service(self, endpoint_yaml):
        """
            This will return the docker registry service that is being served
            inside of kubernetes.
        """

        print "\nFinding the Docker Registry pods via Openshift API calls..."

        endpoints = yaml.safe_load(endpoint_yaml)
        self.docker_port = str(endpoints['subsets'][0]['ports'][0]['port'])

        self.docker_hosts = []
        for address in endpoints['subsets'][0]['addresses']:
            self.docker_hosts.append(address['ip'])

    def registry_health_check(self):
        """
            Check the registry's / URL

            In v3.0.2.0, http://registry.url/healthz worked. The '/healthz' was
              something added by openshift to the docker registry. This should return a http status
              code of 200 and text of {} (empty json).

            In 3.1.1 and on, '/' should work and return a 200 to
              indicate that the registry is up and running. Please see the following url for
              more info.  Look under load balancer health checks:
            https://github.com/docker/distribution/blob/master/docs/deploying.md#running-a-domain-registry
        """

        healthy_registries = 0

        for host in self.docker_hosts:
            try:
                docker_registry_url = "%s://%s:%s/" %(self.docker_protocol, host, self.docker_port)
                print "\nPerforming registry check on URL: %s\n" % docker_registry_url
                response = urllib2.urlopen(docker_registry_url, timeout=20)

                if response.getcode() == 200:
                    healthy_registries += 1

                if response.getcode() == 404:
                    docker_registry_url = "%s://%s:%s/healthz" %(self.docker_protocol, host, self.docker_port)

                    print "\nPerforming registry check on URL: %s\n" % docker_registry_url

                    response = urllib2.urlopen(docker_registry_url, timeout=20)

                    if response.getcode() == 200 and response.readline().startswith('{}'):
                        healthy_registries += 1

            except urllib2.URLError, e:
                print "Error connecting to {}".format(docker_registry_url)

        healthy_pct = 0

        if len(self.docker_hosts) > 0:
            healthy_pct = (healthy_registries / len(self.docker_hosts) *100)

        print "\n%s of %s registries are healthy\n" %(healthy_registries, len(self.docker_hosts))

        self.zagg_sender.add_zabbix_keys({'openshift.master.registry.healthy_pct' : healthy_pct})

if __name__ == '__main__':
    ODRC = OpenshiftDockerRegigtryChecker()
    ODRC.run()
