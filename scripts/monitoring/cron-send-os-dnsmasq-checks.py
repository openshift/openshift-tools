#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Send dnsmasq checks to Zagg

  Openshift uses dnsmasq to locate provide DNS caching on the nodes.

  This can be tested manually with dig from the command line the form:

  $ dig @<instance_internal_ip> www.redhat.com A
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
from dns import resolver
from dns import exception as dns_exception
from openshift_tools.monitoring.metric_sender import MetricSender
import socket

class DnsmasqZaggClient(object):
    """ Checks for the dnsmasq local DNS cache """

    def __init__(self):
        self.args = None
        self.metric_sender = None
        self.dns_host_ip = socket.gethostbyname(socket.gethostname())
        self.dns_port = 53

    def run(self):
        """  Main function to run the check """

        self.parse_args()
        self.metric_sender = MetricSender(verbose=self.args.verbose, debug=self.args.debug)

        if self.check_dns_port_alive():
            self.do_dns_check()

        self.metric_sender.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Network metric sender')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

    def check_dns_port_alive(self):
        """ Verify that the DNS port (TCP 53) is alive """

        print "\nPerforming DNS port check..."

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((self.dns_host_ip, self.dns_port))
            s.close()

            print "\ndnsmasq host: %s, port: %s is OPEN" % (self.dns_host_ip, self.dns_port)
            print "================================================\n"
            self.metric_sender.add_metric({'dnsmasq.port.open' : 1})

            return True

        except socket.error, e:
            print "\ndnsmasq host: %s, port: %s is CLOSED" % (self.dns_host_ip, self.dns_port)
            print "Python Error: %s" % e
            print "================================================\n"
            self.metric_sender.add_metric({'dnsmasq.port.open' : 0})

            return False
    def do_dns_check(self):
        """ perform DNS checks against dnsmasq service """

        print "\nPerforming DNS queries against dnsmasq...\n"

        dns_resolver = resolver.Resolver(configure=False)
        dns_resolver.nameservers.append(self.dns_host_ip)

        # Set dns_check to 1 (good) by default
        dns_check = 1

        name_to_resolve = 'www.redhat.com'

        try:
            dns_answer = dns_resolver.query(name_to_resolve, 'A')
        except dns_exception.DNSException as e:
            print "Failed DNS lookup of %s. Error: %s" % (name_to_resolve, e)
            print "\nTroubleshoot command: dig @%s %s A\n" % (self.dns_host_ip, name_to_resolve)
            dns_check = 0
            # break

        if self.args.verbose:
            print "\nQueryring for A record of %s on server %s" %(name_to_resolve, self.dns_host_ip)
            print "DNS Answer:       %s" % dns_answer.rrset[0].address

        print "================================================\n"

        self.metric_sender.add_metric({'dnsmasq.query' : dns_check})

if __name__ == '__main__':
    ONDZC = DnsmasqZaggClient()
    ONDZC.run()
