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
import json
import subprocess

# pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender
# pylint: enable=import-error
# pylint think check_fluentd is too complex
#pylint: disable=too-many-branches
#pylint: disable=too-many-arguments
#pylint: disable=no-init

class RedirectHandler(urllib2.HTTPRedirectHandler):
    """docstring for RedirctHandler"""
    def http_error_301(self, req, fp, code, msg, headers):
        '''pass 301 error dirrectly'''
        pass
    def http_error_302(self, req, fp, code, msg, headers):
        '''pass 302 error dirrectly'''
        pass

class OpenshiftLoggingStatus(object):
    '''
        This is a check for the entire EFK stack shipped with OCP
    '''
    def __init__(self):
        ''' Initialize OpenShiftLoggingStatus class '''
        self.metric_sender = None
        self.oc = None
        self.args = None
        self.es_pods = []
        self.fluentd_pods = []

        es_cert = '/etc/elasticsearch/secret/admin-'
        self.es_curl = "curl -s --cert {}cert --key {}key --cacert {}ca -XGET ".format(es_cert, es_cert, es_cert)

    def parse_args(self):
        ''' Parse arguments passed to the script '''
        parser = argparse.ArgumentParser(description='OpenShift Cluster Logging Checker')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose output')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
        parser.add_argument('--use-service-ip', action='store_true', default=False,\
                help='use this if kibana can be access by service ip')

        self.args = parser.parse_args()

    def get_pods(self):
        ''' Get all pods and filter them in one pass '''
        pods = self.oc.get_pods()
        for pod in pods['items']:
            if pod['status']['phase'] == 'Failed':
                continue

            if 'component' in pod['metadata']['labels']:
                # Get ES pods
                if pod['metadata']['labels']['component'] == 'es':
                    self.es_pods.append(pod)
                elif pod['metadata']['labels']['component'] == 'fluentd':
                    self.fluentd_pods.append(pod)

    def check_elasticsearch(self):
        ''' Various checks for elasticsearch '''
        es_status = {}
        es_status['single_master'] = None
        es_master_name = None
        es_status['pods'] = {}
        for pod in self.es_pods:
            pod_dc = pod['metadata']['labels']['deploymentconfig']
            pod_name = pod['metadata']['name']
            es_status['pods'][pod_dc] = {}


            cluster_health = self.check_elasticsearch_cluster_health(pod_name)
            if cluster_health['status'] == 'green':
                health_n = 2
            elif cluster_health['status'] == 'yellow':
                health_n = 1
            else:
                health_n = 0

            es_status['pods'][pod_dc]['elasticsearch_health'] = health_n
            es_status['pods'][pod_dc]['elasticsearch_active_primary_shards'] = cluster_health['active_primary_shards']
            es_status['pods'][pod_dc]['elasticsearch_pending_task_queue_depth'] = \
              cluster_health['number_of_pending_tasks']
            es_status['pods'][pod_dc]['disk'] = self.check_elasticsearch_diskspace(pod_name)


            # Compare the master across all ES nodes to see if we have split brain
            curl_cmd = "{} 'https://localhost:9200/_cat/master'".format(self.es_curl)
            es_master = "exec -c elasticsearch -ti {} -- {}".format(pod_name, curl_cmd)
            master_name = self.oc.run_user_cmd(es_master).split(' ')[1]

            if es_status['single_master'] is None:
                es_status['single_master'] = 1
                es_master_name = master_name
            elif es_master_name != master_name:
                es_status['single_master'] = 0

        # fix for 3.4 logging where es_master_name is getting set to an ip.
        # so we set a try check around incase it fails just so it keeps working for 3.3
        for pod in self.es_pods:
            try:
                if pod['status']['podIP'] == es_master_name:
                    es_master_name = pod['metadata']['name']
            except:
                continue

        # get cluster nodes
        curl_cmd = "{} 'https://localhost:9200/_nodes'".format(self.es_curl)
        node_cmd = "exec -c elasticsearch -ti {} -- {}".format(es_master_name, curl_cmd)
        cluster_nodes = json.loads(self.oc.run_user_cmd(node_cmd))['nodes']
        es_status['all_nodes_registered'] = 1
        # The internal ES node name is a random string we do not track anywhere
        # pylint: disable=unused-variable
        for node, data in cluster_nodes.items():
        # pylint: enable=unused-variable
            has_matched = False
            for pod in self.es_pods:
                if data['host'] == pod['metadata']['name'] or data['host'] == pod['status']['podIP']:
                    has_matched = True
                    break

            if has_matched is False:
                es_status['all_nodes_registered'] = 0

        return es_status

    def check_elasticsearch_cluster_health(self, es_pod):
        ''' Exec into the elasticsearch pod and check the cluster health '''
        try:
            curl_cmd = "{} 'https://localhost:9200/_cluster/health?pretty=true'".format(self.es_curl)
            cluster_health = "exec -c elasticsearch -ti {} -- {}".format(es_pod, curl_cmd)
            health_res = json.loads(self.oc.run_user_cmd(cluster_health))

            return health_res

        except:
            # The check failed so ES is in a bad state
            return 0

    def check_elasticsearch_diskspace(self, es_pod):
        ''' Exec into a elasticsearch pod and query the diskspace '''
        results = {}
        try:
            disk_used = 0
            disk_free = 0
            trash_var = 0

            disk_output = self.oc.run_user_cmd("exec -c elasticsearch -ti {} -- df".format(es_pod)).split(' ')
            disk_output = [x for x in disk_output if x]
            for item in disk_output:
                if "/elasticsearch/persistent" not in item:
                    disk_used = disk_free
                    disk_free = trash_var
                    trash_var = item
                else:
                    break

            results['used'] = int(disk_used)
            results['free'] = int(disk_free)
        except:
            results['used'] = int(0)
            results['free'] = int(0)

        return results

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

        # Make sure fluentd is on all the nodes and the pods are running
        fluentd_status['number_expected_pods'] = len(fluentd_nodes)
        fluentd_status['number_pods'] = len(self.fluentd_pods)
        fluentd_status['node_mismatch'] = 0
        fluentd_status['running'] = 1

        for pod in self.fluentd_pods:
            node_matched = False

            try:
                if pod['status']['containerStatuses'][0]['ready'] is False:
                    fluentd_status['running'] = 0
            # do not want to see too much info if pod outofcpu
            except KeyError:
                fluentd_status['running'] = 0

            # If there is already a problem don't worry about looping over the remaining pods/nodes
            for node in fluentd_nodes:
                internal_ip = ""
                for address in node['status']['addresses']:
                    if address['type'] == "InternalIP":
                        internal_ip = address['address']

                try:
                    if node['metadata']['labels']['kubernetes.io/hostname'] == pod['spec']['host']:
                        node_matched = True
                        break

                    raise ValueError('')
                except:
                    if internal_ip == pod['spec']['nodeName'] or node['metadata']['name'] == pod['spec']['nodeName']:
                        node_matched = True
                        break

            if node_matched is False:
                fluentd_status['node_mismatch'] = 1
                break


        return fluentd_status

    def get_kibana_url(self):
        ''' Get the kibana url to access '''
        kibana_url = ""
        if self.args.use_service_ip:
            service = self.oc.get_service('logging-kibana')['spec']['clusterIP']
            kibana_url = "https://{}/".format(service)
        else:
            route = self.oc.get_route('logging-kibana')['status']['ingress'][0]['host']
            kibana_url = "https://{}/".format(route)

        return kibana_url

    def check_kibana(self):
        ''' Check to see if kibana is up and working '''
        kibana_status = {}

        # Get logging url
        kibana_url = self.get_kibana_url()

        # Disable SSL to work around self signed clusters
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # Verify that the url is returning a valid response
        kibana_status['site_up'] = 0
        kibana_status['response_code'] = 0

        debug_handler = urllib2.HTTPHandler(debuglevel=1)
        opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx), debug_handler, RedirectHandler)
        try:
            # get response code from kibana
            u = kibana_status['response_code'] = opener.open(kibana_url, timeout=10)
            kibana_status['response_code'] = u.getcode()

        except urllib2.HTTPError, e:
            kibana_status['response_code'] = e.code
        except urllib2.URLError, e:
            kibana_status['response_code'] = '100'
        else:
            kibana_status['response_code'] = '100'
        # accept 401 because we can't auth: https://bugzilla.redhat.com/show_bug.cgi?id=1466496
        if 200 <= kibana_status['response_code'] <= 401:
            kibana_status['site_up'] = 1

        return kibana_status

    def report_to_zabbix(self, logging_status):
        ''' Report all of our findings to zabbix '''
        self.metric_sender.add_dynamic_metric('openshift.logging.elasticsearch.pods',
                                              '#OSO_METRICS',
                                              logging_status['elasticsearch']['pods'].keys())
        for item, data in logging_status.iteritems():
            if item == "fluentd":
                self.metric_sender.add_metric({
                    'openshift.logging.fluentd.running': data['running'],
                    'openshift.logging.fluentd.number_pods': data['number_pods'],
                    'openshift.logging.fluentd.node_mismatch': data['node_mismatch'],
                    'openshift.logging.fluentd.number_expected_pods': data['number_expected_pods']
                })
            elif item == "kibana":
                self.metric_sender.add_metric({'openshift.logging.kibana.response_code': data['response_code']})
                self.metric_sender.add_metric({'openshift.logging.kibana.site_up': data['site_up']})
            elif item == "elasticsearch":
                self.metric_sender.add_metric({
                    'openshift.logging.elasticsearch.single_master': data['single_master'],
                    'openshift.logging.elasticsearch.all_nodes_registered': data['all_nodes_registered']
                })
                for pod, value in data['pods'].iteritems():
                    self.metric_sender.add_metric({
                        "openshift.logging.elasticsearch.pod_health[%s]" %(pod): value['elasticsearch_health'],
                        "openshift.logging.elasticsearch.pod_active_primary_shards[%s]" %(pod): \
                            value['elasticsearch_active_primary_shards'],
                        "openshift.logging.elasticsearch.pod_pending_task_queue_depth[%s]" %(pod): \
                            value['elasticsearch_pending_task_queue_depth'],
                        "openshift.logging.elasticsearch.disk_free_pct[%s]" %(pod): \
                            value['disk']['free'] * 100 / (value['disk']['free'] + value['disk']['used'] + 1)
                    })
        self.metric_sender.send_metrics()

    def get_logging_namespace(self):
        ''' Determine which logging namespace is in use '''
        # Assume the correct namespace is 'openshift-logging' and fall back to 'logging'
        # if that assumption ends up being wrong.
        oc_client = OCUtil(namespace='openshift-logging', config_file='/tmp/admin.kubeconfig', verbose=self.args.verbose)
        try:
            oc_client.get_dc('logging-kibana')
            # If the previous call didn't throw an exception, logging is deployed in this namespace.
            return 'openshift-logging'
        except subprocess.CalledProcessError:
            return 'logging'

    def run(self):
        ''' Main function that runs the check '''
        self.parse_args()
        self.metric_sender = MetricSender(verbose=self.args.verbose, debug=self.args.debug)
        self.oc = OCUtil(namespace=self.get_logging_namespace(), config_file='/tmp/admin.kubeconfig', verbose=self.args.verbose)
        self.get_pods()

        logging_status = {}
        script_failed = 0 # everything fine
        try:
            logging_status['elasticsearch'] = self.check_elasticsearch()
            logging_status['fluentd'] = self.check_fluentd()
            logging_status['kibana'] = self.check_kibana()
            self.report_to_zabbix(logging_status)
        except:
            script_failed = 1 # something wrong

        mts = MetricSender(verbose=self.args.verbose)
        mts.add_metric({'openshift.master.logging.elasticsearch.script.status': script_failed})
        mts.send_metrics()



if __name__ == '__main__':
    OSLS = OpenshiftLoggingStatus()
    OSLS.run()
