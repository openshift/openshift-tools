#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Send Openshift cluster capacity to Zagg
'''
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
# pylint flaggs import errors, as the bot doesn't know out openshift-tools libs
#pylint: disable=import-error

import argparse
from openshift_tools.web.openshift_rest_api import OpenshiftRestApi
from openshift_tools.monitoring.zagg_sender import ZaggSender
import sqlite3
import yaml
from openshift_tools.conversions import to_bytes, to_milicores

class OpenshiftClusterCapacity(object):
    ''' Checks for cluster capacity '''

    def __init__(self):
        self.args = None
        self.zagg_sender = None
        self.ora = None
        self.sql_conn = None
        self.zbx_key_prefix = "openshift.master.cluster.compute_nodes."

    def run(self):
        '''  Main function to run the check '''

        self.parse_args()
        self.zagg_sender = ZaggSender(verbose=self.args.verbose,
                                      debug=self.args.debug)

        master_cfg = []
        with open(self.args.master_config, 'r') as yml:
            master_cfg = yaml.load(yml)
        self.ora = OpenshiftRestApi(host=master_cfg['oauthConfig']['masterURL'],
                                    verify_ssl=True)

        self.cluster_capacity()

        if not self.args.dry_run:
            self.zagg_sender.send_metrics()

    def parse_args(self):
        ''' parse the args from the cli '''

        parser = argparse.ArgumentParser(description='Cluster capacity sender')
        parser.add_argument('--master-config',
                            default='/etc/origin/master/master-config.yaml',
                            help='Location of OpenShift master-config.yml file')
        parser.add_argument('-v', '--verbose', action='store_true',
                            default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true',
                            default=None, help='Debug?')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Do not sent results to Zabbix')

        self.args = parser.parse_args()

    def load_nodes(self):
        ''' load nodes into SQL '''

        self.sql_conn.execute('''CREATE TABLE nodes
                                 (name text, type text, api text,
                                  max_cpu integer, max_memory integer,
                                  max_pods integer)''')
        response = self.ora.get('/api/v1/nodes')

        for new_node in response['items']:
            # Skip nodes not in 'Ready' state
            node_ready = False
            for condition in new_node['status']['conditions']:
                if condition['type'] == 'Ready' and \
                   condition['status'] == 'True':
                    node_ready = True
            if not node_ready:
                continue

            # Skip unschedulable nodes
            if new_node['spec'].get('unschedulable'):
                continue

            node = {}
            node['name'] = new_node['metadata']['name']
            node['type'] = new_node['metadata']['labels'].get('type', 'unknown')
            node['api'] = new_node['metadata']['selfLink']

            if 'allocatable' in new_node['status']:
                cpu = new_node['status']['allocatable']['cpu']
                mem = new_node['status']['allocatable']['memory']
                node['max_pods'] = int(new_node['status']['allocatable']['pods'])
            else:
                cpu = new_node['status']['capacity']['cpu']
                mem = new_node['status']['capacity']['memory']
                node['max_pods'] = int(new_node['status']['capacity']['pods'])

            node['max_cpu'] = to_milicores(cpu)
            node['max_memory'] = to_bytes(mem)

            if self.args.debug:
                print "Adding node: {}".format(str(node))

            self.sql_conn.execute('INSERT INTO nodes VALUES (?,?,?,?,?,?)',
                                  (node['name'], node['type'], node['api'],
                                   node['max_cpu'], node['max_memory'],
                                   node['max_pods']))

    @staticmethod
    def load_container_limits(pod, containers):
        ''' process/store container limits data '''

        for container in containers:
            if 'limits' in container['resources']:
                pod['cpu_limits'] = pod.get('cpu_limits', default=0) # in case below if is never true
                cpu = container['resources']['limits'].get('cpu')
                if cpu:
                    pod['cpu_limits'] = pod.get('cpu_limits', 0) + \
                                        to_milicores(cpu)

                pod['memory_limits'] = pod.get('memory_limits', default=0) # in case below if is never true
                mem = container['resources']['limits'].get('memory')
                if mem:
                    pod['memory_limits'] = pod.get('memory_limits', 0) + \
                                           to_bytes(mem)

            if 'requests' in container['resources']:
                pod['cpu_requests'] = pod.get('cpu_requests', default=0) # in case below if is never true
                cpu = container['resources']['requests'].get('cpu')
                if cpu:
                    pod['cpu_requests'] = pod.get('cpu_requests', 0) + \
                                          to_milicores(cpu)

                pod['memory_requests'] = pod.get('memory_requests', default=0) # in case below if is never true
                mem = container['resources']['requests'].get('memory')
                if mem:
                    pod['memory_requests'] = pod.get('memory_requests', 0) + \
                                             to_bytes(mem)

    def load_pods(self):
        ''' put pod details into db '''

        self.sql_conn.execute('''CREATE TABLE pods
                                 (name text, namespace text, api text,
                                  cpu_limits integer, cpu_requests integer,
                                  memory_limits integer,
                                  memory_requests integer, node text)''')
        response = self.ora.get('/api/v1/pods')

        for new_pod in response['items']:
            if new_pod['status']['phase'] != 'Running':
                continue

            pod = {}
            pod['name'] = new_pod['metadata']['name']
            pod['namespace'] = new_pod['metadata']['namespace']
            pod['api'] = new_pod['metadata']['selfLink']
            pod['node'] = new_pod['spec']['nodeName']
            self.load_container_limits(pod, new_pod['spec']['containers'])

            self.sql_conn.execute('INSERT INTO pods VALUES (?,?,?,?,?,?,?,?)',
                                  (pod['name'], pod['namespace'], pod['api'],
                                   pod.get('cpu_limits'),
                                   pod.get('cpu_requests'),
                                   pod.get('memory_limits'),
                                   pod.get('memory_requests'),
                                   pod['node']))

    def get_largest_pod(self):
        ''' return single largest memory request number for all running pods '''

        max_pod = 0
        for row in self.sql_conn.execute('''SELECT MAX(memory_requests)
                                            FROM pods, nodes
                                            WHERE pods.node=nodes.name
                                              AND nodes.type="compute"'''):
            max_pod = row[0]

        return max_pod

    def how_many_schedulable(self, node_size):
        ''' return how many pods with memory request 'node_size' can be scheduled '''

        nodes = {}

        # get max mem for each compute node
        for row in self.sql_conn.execute('''SELECT nodes.name, nodes.max_memory
                                            FROM nodes
                                            WHERE nodes.type="compute"'''):
            nodes[row[0]] = {'max_memory': row[1],
                             # set memory_allocated to '0' because node may have
                             # no pods running, and next SQL query below will
                             # leave this field unpopulated
                             'memory_scheduled': 0}

        # get memory requests for all pods on all compute nodes
        for row in self.sql_conn.execute('''SELECT nodes.name,
                                                   SUM(pods.memory_requests)
                                            FROM pods, nodes
                                            WHERE pods.node=nodes.name
                                              AND nodes.type="compute"
                                            GROUP BY nodes.name'''):
            nodes[row[0]]['memory_scheduled'] = row[1]

        schedulable = 0
        for node in nodes.keys():
            # TODO: Some containers from `oc get pods --all-namespaces -o json` don't have resources scheduled, causing memory_scheduled == 0
            available = nodes[node]['max_memory'] - \
                        nodes[node]['memory_scheduled']
            num = available / node_size
            # ignore negative number (overcommitted nodes)
            if num > 0:
                schedulable += num

        return schedulable

    def get_compute_nodes_max_schedulable_cpu(self):
        ''' calculate total schedulable CPU (in milicores) for all compute nodes '''
        max_cpu = 0
        for row in self.sql_conn.execute('''SELECT SUM(nodes.max_cpu)
                                            FROM nodes
                                            WHERE nodes.type="compute" '''):
            max_cpu = row[0]
        return max_cpu

    def get_compute_nodes_max_schedulable_mem(self):
        ''' calculate total schedulable memory for all compute nodes '''
        max_mem = 0
        for row in self.sql_conn.execute('''SELECT SUM(nodes.max_memory)
                                            FROM nodes
                                            WHERE nodes.type="compute" '''):
            max_mem = row[0]
        return max_mem

    def get_compute_nodes_scheduled_cpu(self):
        ''' calculate cpu scheduled to pods
            (total requested and percentage of cluster-wide total) '''
        max_cpu = self.get_compute_nodes_max_schedulable_cpu()
        cpu_requests_for_all_pods = 0
        for row in self.sql_conn.execute('''SELECT SUM(pods.cpu_requests)
                                            FROM pods, nodes
                                            WHERE pods.node = nodes.name
                                              AND nodes.type = "compute" '''):
            cpu_requests_for_all_pods = row[0]

        cpu_scheduled_as_pct = 100.0 * cpu_requests_for_all_pods / max_cpu

        cpu_unscheduled = max_cpu - cpu_requests_for_all_pods
        cpu_unscheduled_as_pct = 100.0 * cpu_unscheduled / max_cpu

        return (cpu_requests_for_all_pods, cpu_scheduled_as_pct,
                cpu_unscheduled, cpu_unscheduled_as_pct)

    def get_compute_nodes_scheduled_mem(self):
        ''' calculate mem allocated to pods
            (total requested and percentage of cluster-wide total) '''
        max_mem = self.get_compute_nodes_max_schedulable_mem()
        mem_requests_for_all_pods = 0
        for row in self.sql_conn.execute('''SELECT SUM(pods.memory_requests)
                                            FROM pods, nodes
                                            WHERE pods.node = nodes.name
                                              AND nodes.type = "compute" '''):
            mem_requests_for_all_pods = row[0]

        mem_scheduled_as_pct = 100.0 * mem_requests_for_all_pods / max_mem

        mem_unscheduled = max_mem - mem_requests_for_all_pods
        mem_unscheduled_as_pct = 100.0 * mem_unscheduled / max_mem

        return (mem_requests_for_all_pods, mem_scheduled_as_pct, mem_unscheduled, mem_unscheduled_as_pct)

    def get_oversub_cpu(self):
        ''' return percentage oversubscribed based on CPU limits on runing pods '''
        max_cpu = self.get_compute_nodes_max_schedulable_cpu()
        pod_cpu_limits = 0

        # get cpu limits for all running pods
        for row in self.sql_conn.execute('''SELECT SUM(pods.cpu_limits)
                                            FROM pods, nodes
                                            WHERE pods.node = nodes.name
                                              AND nodes.type = "compute" '''):
            pod_cpu_limits = row[0]

        return ((float(pod_cpu_limits)/max_cpu) * 100.0) - 100

    def get_oversub_mem(self):
        ''' return percentage oversubscribed based on memory limits on running pods '''
        max_mem = self.get_compute_nodes_max_schedulable_mem()
        pod_mem_limits = 0

        # get mem limits for all running pods
        for row in self.sql_conn.execute('''SELECT SUM(pods.memory_limits)
                                            FROM pods, nodes
                                            WHERE pods.node = nodes.name
                                              AND nodes.type = "compute" '''):
            pod_mem_limits = row[0]

        return ((float(pod_mem_limits)/max_mem) * 100.0) - 100

    def do_cpu_stats(self):
        ''' gather and report CPU statistics '''
         # CPU items
        zbx_key_max_schedulable_cpu = self.zbx_key_prefix + "max_schedulable.cpu"
        zbx_key_scheduled_cpu = self.zbx_key_prefix + "scheduled.cpu"
        zbx_key_scheduled_cpu_pct = self.zbx_key_prefix + "scheduled.cpu_pct"
        zbx_key_unscheduled_cpu = self.zbx_key_prefix + "unscheduled.cpu"
        zbx_key_unscheduled_cpu_pct = self.zbx_key_prefix + "unscheduled.cpu_pct"
        zbx_key_oversub_cpu_pct = self.zbx_key_prefix + "oversubscribed.cpu_pct"

        print "CPU Stats:"
        max_schedulable_cpu = self.get_compute_nodes_max_schedulable_cpu()
        self.zagg_sender.add_zabbix_keys({zbx_key_max_schedulable_cpu:
                                          max_schedulable_cpu})

        scheduled_cpu, scheduled_cpu_pct, unscheduled_cpu, unscheduled_cpu_pct = self.get_compute_nodes_scheduled_cpu()
        oversub_cpu_pct = self.get_oversub_cpu()

        print "  Scheduled CPU for compute nodes:\t\t\t" + \
              "{:>15} milicores".format(scheduled_cpu)
        print "  Unscheduled CPU for compute nodes:\t\t\t" + \
              "{:>15} milicores".format(unscheduled_cpu)
        print "  Maximum (total) schedulable CPU for compute " + \
              "nodes:\t{:>15} milicores".format(max_schedulable_cpu)
        print "  Percent scheduled CPU for compute nodes:\t\t\t" + \
              "{:.2f}%".format(scheduled_cpu_pct)
        print "  Percent unscheduled CPU for compute nodes:\t\t\t" + \
              "{:.2f}%".format(unscheduled_cpu_pct)
        print "  Percent oversubscribed CPU for compute nodes: \t\t" + \
              "{:.2f}%".format(oversub_cpu_pct)
        self.zagg_sender.add_zabbix_keys({zbx_key_scheduled_cpu: scheduled_cpu})
        self.zagg_sender.add_zabbix_keys({zbx_key_scheduled_cpu_pct:
                                          int(scheduled_cpu_pct)})
        self.zagg_sender.add_zabbix_keys({zbx_key_unscheduled_cpu: unscheduled_cpu})
        self.zagg_sender.add_zabbix_keys({zbx_key_unscheduled_cpu_pct:
                                          int(unscheduled_cpu_pct)})
        self.zagg_sender.add_zabbix_keys({zbx_key_oversub_cpu_pct:
                                          int(oversub_cpu_pct)})

    def do_mem_stats(self):
        ''' gather and report memory statistics '''
        # Memory items
        zbx_key_max_schedulable_mem = self.zbx_key_prefix + "max_schedulable.mem"
        zbx_key_scheduled_mem = self.zbx_key_prefix + "scheduled.mem"
        zbx_key_scheduled_mem_pct = self.zbx_key_prefix + "scheduled.mem_pct"
        zbx_key_unscheduled_mem = self.zbx_key_prefix + "unscheduled.mem"
        zbx_key_unscheduled_mem_pct = self.zbx_key_prefix + "unscheduled.mem_pct"
        zbx_key_oversub_mem_pct = self.zbx_key_prefix + "oversubscribed.mem_pct"

        print "\nMemory Stats:"
        max_schedulable_mem = self.get_compute_nodes_max_schedulable_mem()
        self.zagg_sender.add_zabbix_keys({zbx_key_max_schedulable_mem:
                                          max_schedulable_mem})

        scheduled_mem, scheduled_mem_pct, unscheduled_mem, unscheduled_mem_pct = self.get_compute_nodes_scheduled_mem()
        oversub_mem_pct = self.get_oversub_mem()
        print "  Scheduled mem for compute nodes:\t\t\t" + \
              "{:>20} bytes".format(scheduled_mem)
        print "  Unscheduled mem for compute nodes:\t\t\t" + \
              "{:>20} bytes".format(unscheduled_mem)
        print "  Maximum (total) schedulable memory for compute nodes:\t" + \
              "{:>20} bytes".format(max_schedulable_mem)
        print "  Percent scheduled mem for compute nodes:\t\t\t" + \
              "{:.2f}%".format(scheduled_mem_pct)
        print "  Percent unscheduled mem for compute nodes:\t\t\t" + \
              "{:.2f}%".format(unscheduled_mem_pct)
        print "  Percent oversubscribed mem for compute nodes: \t\t" + \
              "{:.2f}%".format(oversub_mem_pct)
        self.zagg_sender.add_zabbix_keys({zbx_key_scheduled_mem: scheduled_mem})
        self.zagg_sender.add_zabbix_keys({zbx_key_scheduled_mem_pct:
                                          int(scheduled_mem_pct)})
        self.zagg_sender.add_zabbix_keys({zbx_key_unscheduled_mem: unscheduled_mem})
        self.zagg_sender.add_zabbix_keys({zbx_key_unscheduled_mem_pct:
                                          int(unscheduled_mem_pct)})
        self.zagg_sender.add_zabbix_keys({zbx_key_oversub_mem_pct:
                                          int(oversub_mem_pct)})


    def cluster_capacity(self):
        ''' check capacity of compute nodes on cluster'''

        # Other zabbix items
        zbx_key_max_pods = "openshift.master.cluster.max_mem_pods_schedulable"

        self.sql_conn = sqlite3.connect(':memory:')

        self.load_nodes()
        self.load_pods()

        self.do_cpu_stats()
        self.do_mem_stats()

        print "\nOther stats:"
        largest = self.get_largest_pod()
        if self.args.debug:
            print "  Largest memory pod: {}".format(largest)

        schedulable = self.how_many_schedulable(largest)
        print "  Number of max-size nodes schedulable:\t\t\t\t{}".format(schedulable)
        self.zagg_sender.add_zabbix_keys({zbx_key_max_pods: schedulable})

if __name__ == '__main__':
    OCC = OpenshiftClusterCapacity()
    OCC.run()
