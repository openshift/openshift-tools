#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Send Openshift Master SkyDNS metric checks to Zagg

  Openshift uses SkyDNS to locate services inside of the cluster.

  Openshift implements SkyDNS a bit different.  Normally SkyDNS uses etcd as a backend
  for the DNS data to be stored.  Openshift uses a special SkyDNS provider to map
  Openshift services to IP's.  More info can be found by looking at the source code here:

  https://github.com/openshift/origin/blob/master/pkg/dns/serviceresolver.go

  In short, the Openshift service name has a name, namespace and IP. The custom provider
  can return many different variations of these for services, endpoints, an ports.  The
  variation that is used within this script is in the form of:

  <name>.<namespace>.svc.cluster.local

  This can be tested manually with dig from the command line the form:

  $ dig @<nameserver> <name>.<namespace>.svc.cluster.local A

  In this script, I am assuming that each Openshift service will have one and only one IP.
  This *could* change and we will need to examine each of the IP's returned from Openshift
  and SkyDNS
'''
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
# Bot doesn't support openshift_tools libs
#pylint: disable=import-error

import argparse
import dns
from openshift_tools.web.openshift_rest_api import OpenshiftRestApi
from openshift_tools.monitoring.zagg_sender import ZaggSender
import socket

class OpenshiftSkyDNSZaggClient(object):
    """ Checks for the Openshift Master SkyDNS """

    def __init__(self):
        self.args = None
        self.zagg_sender = None
        self.ora = OpenshiftRestApi()
        self.dns_host = '127.0.0.1'
        self.dns_port = 53
        self.openshift_services = []

    def run(self):
        """  Main function to run the check """

        self.parse_args()
        self.zagg_sender = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)

        if self.check_dns_port_alive():
            self.get_openshift_services()
            self.do_dns_check()

        self.zagg_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Network metric sender')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

    def check_dns_port_alive(self):
        """ Verify that the DNS port (TCP 53) is alive """

        print "\nPerforming Openshift DNS port check..."

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((self.dns_host, self.dns_port))
            s.close()

            print "\nOpenshift SkyDNS host: %s, port: %s is OPEN" % (self.dns_host, self.dns_port)
            print "================================================\n"
            self.zagg_sender.add_zabbix_keys({'openshift.master.skydns.port.open' : 1})

            return True

        except socket.error, e:
            print "\nOpenshift SkyDNS host: %s, port: %s is CLOSED" % (self.dns_host, self.dns_port)
            print "Python Error: %s" % e
            print "================================================\n"
            self.zagg_sender.add_zabbix_keys({'openshift.master.skydns.port.open' : 0})

            return False

    def get_openshift_services(self):
        """ Get a list of Openshift services that can be used to test against SkyDNS """

        print "\nQuerying for Openshift services in the 'default' namespace...\n"

        response = self.ora.get('/api/v1/namespaces/default/services')

        for i in response['items']:
            service = {}
            service['name'] = i['metadata']['name']
            service['namespace'] = i['metadata']['namespace']
            service['ip'] = i['spec']['clusterIP']

            self.openshift_services.append(service)

        if self.args.verbose:
            print "\nOpenshift Services found:\n"
            print "{0:35} {1:25} {2:20}".format("Name", "Namespace", "IP")
            for i in self.openshift_services:
                print "{0:35} {1:25} {2:20}".format(i['name'], i['namespace'], i['ip'])

        print "================================================\n"

    def do_dns_check(self):
        """ perform DNS checks against SkyDNS service """

        print "\nPerforming DNS queries against SkyDNS...\n"

        dns_resolver = dns.resolver.Resolver(configure=False)
        dns_resolver.nameservers.append(self.dns_host)

        # Set dns_check to 1 (good) by default
        dns_check = 1

        for service in self.openshift_services:
            name_to_resolve = service['name'] + '.' + service['namespace'] + '.svc.cluster.local'

            try:
                dns_answer = dns_resolver.query(name_to_resolve, 'A')
            except dns.exception.DNSException as e:
                print "Failed DNS lookup of %s. Error: %s" % (name_to_resolve, e)
                print "\nTroubleshoot command: dig @%s %s A\n" % (self.dns_host, name_to_resolve)
                dns_check = 0
                break

            if self.args.verbose:
                print "\nQueryring for A record of %s on server %s" %(name_to_resolve, self.dns_host)
                print "DNS Answer:       %s" % dns_answer.rrset[0].address
                print "Openshift Answer: %s" % service['ip']

            if dns_answer.rrset[0].address != service['ip']:
                dns_check = 0

        print "================================================\n"

        self.zagg_sender.add_zabbix_keys({'openshift.master.skydns.query' : dns_check})

if __name__ == '__main__':
    OMSZC = OpenshiftSkyDNSZaggClient()
    OMSZC.run()
