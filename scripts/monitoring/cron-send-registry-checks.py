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
import socket
import urllib2
import yaml

class OpenshiftDockerRegigtryChecker(object):
    """ Checks for the Openshift Cluster Docker Registry """

    def __init__(self):
        self.args = None
        self.zagg_sender = None

        self.docker_hosts = []
        self.docker_port = None
        # Assume secure registry
        self.docker_protocol = 'https'
        self.docker_service_ip = None
        self.kubeconfig = None

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
            oc_yaml = ocutil.get_service('docker-registry')
            self.get_registry_service(oc_yaml)
            oc_yaml = ocutil.get_endpoint('docker-registry')
            self.get_registry_endpoints(oc_yaml)
        except Exception as ex:
            print "Problem retreiving registry IPs: %s " % ex.message
            self.zagg_sender.add_zabbix_keys({'openshift.master.registry.healthy_pct' : 0})

        self.registry_service_check()
        self.registry_health_check()

        self.zagg_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Openshift Cluster Docker Registry sender')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

    def get_registry_service(self, service_yaml):
        ''' This will get the service IP of the docker registry '''
        print "\nGetting Docker Registry service IP..."

        service = yaml.safe_load(service_yaml)
        self.docker_service_ip = str(service['spec']['clusterIP'])

    def get_registry_endpoints(self, endpoint_yaml):
        """
            This will return the docker registry endpoint IPs that are being served
            inside of kubernetes.
        """

        print "\nFinding the Docker Registry pods via Openshift API calls..."

        endpoints = yaml.safe_load(endpoint_yaml)
        self.docker_port = str(endpoints['subsets'][0]['ports'][0]['port'])

        self.docker_hosts = []
        for address in endpoints['subsets'][0]['addresses']:
            self.docker_hosts.append(address['ip'])

    def healthy_registry(self, ip_addr, port, secure=True):
        ''' Test a specific registry URL
            In v3.0.2.0, http://registry.url/healthz worked. The '/healthz' was
              something added by openshift to the docker registry. This should return a http status
              code of 200 and text of {} (empty json).

            In 3.1.1 and on, '/' should work and return a 200 to
              indicate that the registry is up and running. Please see the following url for
              more info.  Look under load balancer health checks:
            https://github.com/docker/distribution/blob/master/docs/deploying.md#running-a-domain-registry
        '''

        proto = self.docker_protocol
        if not secure:
            proto = 'http'
        url = '{}://{}:{}/'.format(proto, ip_addr, port)

        try:
            print "Performing Docker Registry check on URL: {}".format(url)
            response = urllib2.urlopen(url, timeout=20)

            if response.getcode() == 200:
                return True
        except urllib2.URLError:
            print "Received error accessing URL: {}".format(url)
        except socket.timeout:
            print "Timed out accessing URL: {}".format(url)

        # Try with /healthz
        try:
            url = url + 'healthz'
            print "Performing Docker Registry check on URL: {}".format(url)
            response = urllib2.urlopen(url, timeout=20)

            if response.getcode() == 200:
                return True
        except urllib2.URLError:
            print "Received error access URL: {}".format(url)
        except socket.timeout:
            print "Timed out accessing URL: {}".format(url)

        # We tried regular and 'healthz' URLs. Registry inaccessible.
        return False

    def registry_service_check(self):
        ''' Test and report on health of Docker Registry service '''

        status = '0'
        if self.healthy_registry(self.docker_service_ip, self.docker_port):
            status = '1'
        elif self.healthy_registry(self.docker_service_ip, self.docker_port,
                                   secure=False):
            status = '1'

        print "\nDocker Registry service status: {}".format(status)

        self.zagg_sender.add_zabbix_keys({'openshift.node.registry.service.ping' : status})

    def registry_health_check(self):
        """
            Check the registry's / URL

       """

        healthy_registries = 0

        for host in self.docker_hosts:
            if self.healthy_registry(host, self.docker_port):
                healthy_registries += 1
            elif self.healthy_registry(host, self.docker_port, secure=False):
                healthy_registries += 1

        healthy_pct = 0

        if len(self.docker_hosts) > 0:
            healthy_pct = (healthy_registries / len(self.docker_hosts) *100)

        print "\n%s of %s registry PODs are healthy\n" %(healthy_registries,
                                                         len(self.docker_hosts))

        self.zagg_sender.add_zabbix_keys({'openshift.node.registry-pods.healthy_pct' : healthy_pct})

if __name__ == '__main__':
    ODRC = OpenshiftDockerRegigtryChecker()
    ODRC.run()
