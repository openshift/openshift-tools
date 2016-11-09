#!/usr/bin/env python
'''
  Send Cluster router checks to Zagg
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#
#   Copyright 2016 Red Hat Inc.
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
# oso modules won't be available to pylint in Jenkins
#pylint: disable=import-error

import argparse
import os
from openshift_tools.monitoring.zagg_sender import ZaggSender
from openshift_tools.monitoring.ocutil import OCUtil
import urllib2

class OpenshiftRouterChecks(object):
    """Checks for the Openshift Router"""

    def __init__(self):
        self.args = None
        self.zgs = None # zagg sender
        self.kubeconfig = None
        self.parse_args()
        self.get_kubeconfig()
        self.ocutil = None

    def get_kubeconfig(self):
        """Find kubeconfig to use for OCUtil"""
        # Default master kubeconfig
        kubeconfig = '/tmp/admin.kubeconfig'
        non_master_kube_dir = '/etc/origin/node'

        if os.path.exists(kubeconfig):
            # If /tmp/admin.kubeconfig exists, use it!
            pass
        elif os.path.isdir(non_master_kube_dir):
            for my_file in os.listdir(non_master_kube_dir):
                if my_file.endswith(".kubeconfig"):
                    kubeconfig = os.path.join(non_master_kube_dir, my_file)

        if self.args.debug:
            print "Using kubeconfig: {}".format(kubeconfig)

        self.kubeconfig = kubeconfig

    def check_all_router_health(self):
        """ Perform defined router health check on all routers """

        discovery_key = "disc.openshift.cluster.router"
        discovery_macro = "#OS_ROUTER"
        router_health_item = "disc.openshift.cluster.router.health"

        router_pods = self.find_router_pods()
        health_report = {}
        for router_name, pod_details in router_pods.iteritems():
            health = self.router_pod_healthy(pod_details)
            if self.args.verbose:
                print "{} healthy: {}\n".format(router_name, health)
            health_report[router_name] = health


        # make dynamic items, and queue up the associated data
        router_names = health_report.keys()
        self.zgs.add_zabbix_dynamic_item(discovery_key, discovery_macro,
                                         router_names, synthetic=True)

        for router_name, health_status in health_report.iteritems():
            zbx_key = "{}[{}]".format(router_health_item, router_name)
            self.zgs.add_zabbix_keys({zbx_key: int(health_status)},
                                     synthetic=True)

    def running_pod_count_check(self):
        """ return hash of deployment configs containing whether the number
            of running pods matches the definition in the deployment config """

        router_pods = self.find_router_pods()

        # get actual running pod count (per DC)
        dc_pod_count = {}
        for _, details in router_pods.iteritems():
            dc_name = details['metadata']['labels']['deploymentconfig']
            dc_pod_count[dc_name] = dc_pod_count.get(dc_name, 0) + 1

        if self.args.debug:
            print "Running pod count: {}".format(dc_pod_count)

        # get expected pod count as defined in each router DC
        expected_pod_count = {}
        for dc_name in dc_pod_count.keys():
            expected_pod_count[dc_name] = self.ocutil.get_dc(dc_name)['spec']['replicas']

        if self.args.debug:
            print "Expected pod count: {}".format(expected_pod_count)

        results = {}
        for dc_name in dc_pod_count.keys():
            results[dc_name] = bool(dc_pod_count[dc_name] == expected_pod_count[dc_name])

        if self.args.verbose or self.args.debug:
            print "DC replica count matching actual counts: {}".format(results)

        return results

    def check_router_replica_count(self):
        """ Check whether the running router replica count is the same
            as what is defined in the deployment config """

        discovery_key = "disc.openshift.cluster.router"
        discovery_macro = "#ROUTER_DC"
        dc_status_item = "disc.openshift.cluster.router.expected_pod_count"

        replica_results = self.running_pod_count_check()

        # make dynamic items, and queue up the associated data
        dc_names = replica_results.keys()
        self.zgs.add_zabbix_dynamic_item(discovery_key, discovery_macro,
                                         dc_names, synthetic=True)

        for dc_name, replica_status in replica_results.iteritems():
            zbx_key = "{}[{}]".format(dc_status_item, dc_name)
            self.zgs.add_zabbix_keys({zbx_key: int(replica_status)},
                                     synthetic=True)

    def run(self):
        """Main function to run the check"""

        self.ocutil = OCUtil(config_file=self.kubeconfig, verbose=self.args.verbose)
        self.zgs = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)

        self.check_all_router_health()
        self.check_router_replica_count()

        if self.args.dry_run:
            self.zgs.print_unique_metrics_key_value()
        else:
            self.zgs.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='Openshift Router sender')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Collect stats, but no report to zabbix')

        self.args = parser.parse_args()


    @staticmethod
    def get_router_health_url(router):
        """ build router healthcheck URL """

        podip = router['status']['podIP']
        port = router['spec']['containers'][0]['livenessProbe']['httpGet']['port']
        path = router['spec']['containers'][0]['livenessProbe']['httpGet']['path']
        url = 'http://{}:{}{}'.format(podip, port, path)

        return url

    @staticmethod
    def router_pod_healthy(router):
        """ ping the health port for router pod health """

        url = OpenshiftRouterChecks.get_router_health_url(router)

        try:
            result = urllib2.urlopen(url).getcode()
            if result == 200:
                return True
            else:
                return False
        except (urllib2.HTTPError, urllib2.URLError):
            return False

    def find_router_pods(self):
        """ return dict of PODs running haproxy (the router pods) """

        router_pods = {}
        for pod in self.ocutil.get_pods()['items']:
            try:
                img = pod['status']['containerStatuses'][0]['image']
                if 'ose-haproxy-router' in img:
                    router_pods[pod['metadata']['name']] = pod
            except KeyError:
                pass

        return router_pods

def main():
    """Perform the router checks"""

    orc = OpenshiftRouterChecks()
    orc.run()


if __name__ == '__main__':
    main()
