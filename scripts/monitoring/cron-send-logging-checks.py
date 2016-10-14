#!/usr/bin/env python
'''
  Send Cluster EFK checks to Zagg
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
#If a check throws an exception it is failed and should alert
#pylint: disable=bare-except
import argparse
import ssl
import urllib2

# pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.zagg_sender import ZaggSender
# pylint: enable=import-error

class OpenshiftLoggingStatus(object):
    '''
        This is a check for the entire EFK stack shipped with OCP
    '''
    def __init__(self):
        ''' Initialize OpenShiftLoggingStatus class '''
        self.logging_ns = "logging"
        self.kubeconfig = '/tmp/admin.kubeconfig'
        self.zagg_sender = None
        self.oc = None
        self.args = None

        es_cert = '/etc/elasticsearch/secret/admin-'
        self.es_curl = "curl --cert {}cert --key {}key --cacert {}ca -XGET ".format(es_cert, es_cert, es_cert)

    def parse_args(self):
        ''' Parse arguments passed to the script '''
        parser = argparse.ArgumentParser(description='OpenShift Cluster Logging Checker')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose output')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

    def check_elasticsearch(self):
        ''' Various checks for elasticsearch '''
        es_status = {}
        es_status['single_master'] = None
        es_master_name = None
        pods = self.oc.get_pods()
        es_pods = []
        es_status['pods'] = {}
        for pod in pods['items']:
            if 'component' in pod['metadata']['labels']:
                # Get ES pods
                if pod['metadata']['labels']['component'] == 'es':
                    es_pods.append(pod)

                    pod_dc = pod['metadata']['labels']['deploymentconfig']
                    pod_name = pod['metadata']['name']
                    es_status['pods'][pod_dc] = {}


                    # exec into a pod and get cluster health
                    curl_cmd = "{} 'https://localhost:9200/_cluster/health?pretty=true'".format(self.es_curl)
                    cluster_health = "exec -ti {} -- {}".format(pod_name, curl_cmd)
                    health_res = self.oc.run_user_cmd(cluster_health)

                    if health_res['status'] == 'green':
                        es_status['pods'][pod_dc]['elasticsearch_health'] = 2
                    elif health_res['status'] == 'yellow':
                        es_status['pods'][pod_dc]['elasticsearch_health'] = 1
                    else:
                        es_status['pods'][pod_dc]['elasticsearch_health'] = 0

                    # Compare the master across all ES nodes to see if we have split brain
                    curl_cmd = "{} 'https://localhost:9200/_cat/master'".format(self.es_curl)
                    es_master = "exec -ti {} -- {}".format(pod_name, curl_cmd)
                    master_name = self.oc.run_user_cmd(es_master).split(' ')[1]

                    if es_status['single_master'] == None:
                        es_status['single_master'] = 1
                        es_master_name = master_name
                    elif es_master_name != master_name:
                        es_status['single_master'] = 0

        # get cluster nodes
        curl_cmd = "{} 'https://localhost:9200/_nodes'".format(self.es_curl)
        node_cmd = "exec -ti {} -- {}".format(es_master_name, curl_cmd)
        cluster_nodes = self.oc.run_user_cmd(node_cmd)['nodes']
        es_status['all_nodes_registered'] = 1
        # The internal ES node name is a random string we do not track anywhere
        # pylint: disable=unused-variable
        for node, data in cluster_nodes.items():
        # pylint: enable=unused-variable
            has_matched = False
            for pod in es_pods:
                if data['host'] == pod['metadata']['name']:
                    has_matched = True

            if has_matched == False:
                es_status['all_nodes_registered'] = 0

        return es_status

    def check_fluentd(self):
        ''' Verify fluentd is running '''
        fluentd_status = {}

        # Get all nodes with fluentd label
        nodes = self.oc.get_nodes()
        fluentd_nodes = []
        for node in nodes['items']:
            if 'logging-infra-fluentd' in node['metadata']['labels']:
                if node['metadata']['labels']['logging-infra-fluentd'] == 'true':
                    fluentd_nodes.append(node)

        # Get all fluentd pods
        pods = self.oc.get_pods()
        fluentd_pods = []
        for pod in pods['items']:
            if 'component' in pod['metadata']['labels']:
                if pod['metadata']['labels']['component'] == 'fluentd':
                    fluentd_pods.append(pod)

        # Make sure fluentd is on all the nodes and the pods are running
        fluentd_status['number_expected_pods'] = len(fluentd_nodes)
        fluentd_status['number_pods'] = len(fluentd_pods)
        fluentd_status['node_mismatch'] = 0
        for node in fluentd_nodes:
            node_matched = False
            for pod in fluentd_pods:
                if node['metadata']['labels']['kubernetes.io/hostname'] == pod['spec']['host']:
                    node_matched = True

            if node_matched == False:
                fluentd_status['node_mismatch'] = 1

        fluentd_status['running'] = 1
        for pod in fluentd_pods:
            if pod['status']['containerStatuses'][0]['ready'] == False:
                fluentd_status['running'] = 0

        return fluentd_status

    def check_kibana(self):
        ''' Check to see if kibana is up and working '''
        kibana_status = {}

        # Get logging url
        route = self.oc.get_route('logging-kibana')['status']['ingress'][0]['host']
        kibana_url = "https://{}/".format(route)

        # Disable SSL to work around self signed clusters
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # Verify that the url is returning a valid response
        kibana_status['site_up'] = 1
        try:
            res = urllib2.urlopen(kibana_url, context=ctx)
            print res

        except urllib2.HTTPError, e:
            if e.code >= 500:
                kibana_status['site_up'] = 0

        return kibana_status

    def report_to_zabbix(self, logging_status):
        ''' Report all of our findings to zabbix '''
        self.zagg_sender.add_zabbix_dynamic_item('openshift.logging.elasticsarch.pods',
                                                 '#OSO_ELASTIC',
                                                 logging_status['elasticsearch']['pods'].keys())
        for item, data in logging_status.iteritems():
            if item == "fluentd":
                self.zagg_sender.add_zabbix_keys({
                    'openshift.logging.fluentd.running': data['running'],
                    'openshift.logging.fluentd.number_pods': data['number_pods'],
                    'openshift.logging.fluentd.node_mismatch': data['node_mismatch'],
                    'openshift.logging.fluentd.number_expected_pods': data['number_expected_pods']
                })
            elif item == "kibana":
                self.zagg_sender.add_zabbix_keys({'openshift.logging.kibana.site_up': data['site_up']})
            elif item == "elasticsearch":
                self.zagg_sender.add_zabbix_keys({
                    'openshift.logging.elasticsearch.single_master': data['single_master'],
                    'openshift.logging.elasticsearch.all_nodes_registered': data['all_nodes_registered']
                })
                for pod, value in data['pods'].iteritems():
                    self.zagg_sender.add_zabbix_keys(
                        {"openshift.logging.elasticsarch.pod_health[%s]" %(pod): value['elasticsearch_health']}
                    )
        self.zagg_sender.send_metrics()

    def run(self):
        ''' Main function that runs the check '''
        self.parse_args()
        self.zagg_sender = ZaggSender(verbose=self.args.verbose, debug=self.args.debug)
        self.oc = OCUtil(namespace='logging', config_file=self.kubeconfig, verbose=self.args.verbose)

        logging_status = {}
        logging_status['elasticsearch'] = self.check_elasticsearch()
        logging_status['fluentd'] = self.check_fluentd()
        logging_status['kibana'] = self.check_kibana()

        self.report_to_zabbix(logging_status)

if __name__ == '__main__':
    OSLS = OpenshiftLoggingStatus()
    OSLS.run()
