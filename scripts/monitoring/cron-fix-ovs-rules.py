#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
'''
  Find and remove "bad" OVS rules/flows.
  A bad flow is one whose action/output references a non-existent port
'''

import re
import subprocess
from subprocess import CalledProcessError

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender

class OVS(object):
    ''' Class to hold details of finding and removing bad OVS rules '''

    def __init__(self):
        # Sanity check to make sure our dependencies are met
        CMD = ["ovs-vsctl", "show"]
        try:
            subprocess.check_call(CMD)
        except (OSError, CalledProcessError):
            print "ovs-ofctl not found or misbehaving"
            exit(1)

        self.ports = None
        self.rules = None

    def get_port_list(self, force_refresh=False):
        ''' Returns list of active/good ports '''
        if force_refresh:
            self.ports = None

        if self.ports:
            return self.ports

        port_list = []
        CMD = ["ovs-ofctl", "-O", "OpenFlow13", "dump-ports-desc", "br0"]
        raw_output = subprocess.check_output(CMD)
        for line in raw_output.split('\n'):
            # Sample output: " 12(veth93a2df3): addr:ca:7b:f4:e4:a1:1d"
            match = re.search(r"^\s*(\d*)\(.*", line)
            if match:
                port_list.append(match.group(1))
        self.ports = port_list

        return self.ports

    def get_rule_list(self, force_refresh=False):
        ''' Returns list of active rules we would care about. We care
            about the case where the assigned cookie is equal to the
            output port '''
        if force_refresh:
            self.rules = None

        if self.rules:
            return self.rules

        rule_list = []
        CMD = ["ovs-ofctl", "-O", "OpenFlow13", "dump-flows", "br0"]
        raw_output = subprocess.check_output(CMD)
        for line in raw_output.split('\n'):
            cookie = line.split(',')[0]
            # Sample output: " cookie=0x11"
            match = re.search(r"\w=0x(.*)", cookie)
            if match:
                cookie = match.group(1)
            else:
                continue

            action = line.split(',')[-1]
            # Sample output: "arp_tpa=10.1.9.9 actions=output:11"
            match = re.search("actions=output:(.*)", action)
            if match:
                action = match.group(1)
            else:
                continue

            # The cookie values that we should be looking at are
            # the ones where the cookie value equals the output
            # port number
            if str(action) == str(cookie):
                rule_list.append(cookie)

        self.rules = rule_list

        return self.rules

    def find_bad_rules(self):
        ''' Return list of rules that reference non-existent ports '''
        # Make sure we're working with rules and ports set
        self.get_rule_list()
        self.get_port_list()

        bad_rules = []
        for rule in self.rules:
            if rule not in self.ports:
                bad_rules.append(rule)

        return bad_rules

    def remove_rules(self, rule_list):
        ''' Remove a list of rules '''
        cmd = ["ovs-ofctl", "-O", "OpenFlow13", "del-flows", "br0"]
        for ovs_rule in rule_list:
            # The trailing '/-1' is the wildcard match
            rule_to_cookie = "cookie=0x{0}/-1".format(ovs_rule)
            cmd.append(rule_to_cookie)
            subprocess.call(cmd)
            cmd.pop()

        # Since rule list has changed, force it to regenerate next time
        self.rules = None

ZBX_KEY = "openshift.node.ovs.stray.rules"

if __name__ == "__main__":
    ovs_fixer = OVS()
    zgs = ZaggSender()

    # Dev says rules before ports since OpenShift will set up ports, then rules
    ovs_fixer.get_rule_list()
    ovs_ports = ovs_fixer.get_port_list()

    ovs_bad_rules = ovs_fixer.find_bad_rules()

    # Report bad/stray rules count before removing
    zgs.add_zabbix_keys({ZBX_KEY: len(ovs_bad_rules)})
    zgs.send_metrics()

    print "Good ports: {0}".format(str(ovs_ports))
    print "Bad rules: {0}".format(str(ovs_bad_rules))

    ovs_fixer.remove_rules(ovs_bad_rules)

    # Refresh list of rules after the removals
    ovs_fixer.get_rule_list(force_refresh=True)

    ovs_bad_rules = ovs_fixer.find_bad_rules()
    print "Bad rules after removals: {0}".format(str(ovs_bad_rules))

    # Report new bad/stray rule count after removal
    zgs.add_zabbix_keys({ZBX_KEY: len(ovs_bad_rules)})
    zgs.send_metrics()
