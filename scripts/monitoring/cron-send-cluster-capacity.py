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

        self.node_capacity()

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
            node = {}
            node['name'] = new_node['metadata']['name']
            node['type'] = new_node['metadata']['labels']['type']
            node['api'] = new_node['metadata']['selfLink']

            cpu = new_node['status']['allocatable']['cpu']
            node['max_cpu'] = to_milicores(cpu)

            mem = new_node['status']['allocatable']['memory']
            node['max_memory'] = to_bytes(mem)

            node['max_pods'] = int(new_node['status']['allocatable']['pods'])

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
                cpu = container['resources']['limits'].get('cpu')
                if cpu:
                    pod['cpu_limits'] = pod.get('cpu_limits', 0) + \
                                        to_milicores(cpu)

                mem = container['resources']['limits'].get('memory')
                if mem:
                    pod['memory_limits'] = pod.get('memory_limits', 0) + \
                                           to_bytes(mem)

            if 'requests' in container['resources']:
                cpu = container['resources']['requests'].get('cpu')
                if cpu:
                    pod['cpu_requests'] = pod.get('cpu_requests', 0) + \
                                          to_milicores(cpu)

                mem = container['resources']['requests'].get('memory')
                if mem:
                    pod['memory_requests'] = pod.get('memory_requests', 0) + \
                                             to_bytes(mem)

    def load_pods(self):
        ''' put pod details into db '''

        self.sql_conn.execute('''CREATE TABLE pods
                                 (name text, namespace text, api text,
                                  cpu_limits integer, cpu_requets integer,
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

    def get_memory_percentage(self):
        ''' calculate pod memory limits as a percentage
            of cluster (compute-node) memory capacity '''

        node_mem = 0
        pod_mem = 0

        for row in self.sql_conn.execute('''SELECT SUM(nodes.max_memory)
                                            FROM nodes
                                            WHERE nodes.type="compute"'''):
            node_mem = row[0]

        for row in self.sql_conn.execute('''SELECT SUM(pods.memory_limits)
                                            FROM pods, nodes
                                            WHERE pods.node=nodes.name
                                              AND nodes.type="compute"'''):
            pod_mem = row[0]

        return float(100) * pod_mem / node_mem

    def get_largest_pod(self):
        ''' return memory limit for largest pod '''

        max_pod = 0
        for row in self.sql_conn.execute('''SELECT MAX(memory_limits)
                                            FROM pods, nodes
                                            WHERE pods.node=nodes.name
                                              AND nodes.type="compute"'''):
            max_pod = row[0]

        return max_pod

    def how_many_schedulable(self, size):
        ''' return how many pods with memory 'size' can be scheduled '''

        nodes = {}

        # get max mem for each compute node
        for row in self.sql_conn.execute('''SELECT nodes.name, nodes.max_memory
                                            FROM nodes
                                            WHERE nodes.type="compute"'''):
            nodes[row[0]] = {'max_memory': row[1]}

        # get memory allocated/granted for each compute node
        for row in self.sql_conn.execute('''SELECT nodes.name,
                                                   SUM(pods.memory_limits)
                                            FROM pods, nodes
                                            WHERE pods.node=nodes.name
                                              AND nodes.type="compute"
                                            GROUP BY nodes.name'''):
            nodes[row[0]]['memory_allocated'] = row[1]

        schedulable = 0
        for node in nodes.keys():
            available = nodes[node]['max_memory'] - \
                        nodes[node]['memory_allocated']
            num = available / size
            # ignore negative number (overcommitted nodes)
            if num > 0:
                schedulable += num

        return schedulable

    def node_capacity(self):
        ''' check capacity of compute nodes '''

        zbx_key_mem_alloc = "openshift.master.cluster.memory_allocation"
        zbx_key_max_pods = "openshift.master.cluster.max_mem_pods_schedulable"

        self.sql_conn = sqlite3.connect(':memory:')

        self.load_nodes()
        self.load_pods()

        memory_percentage = self.get_memory_percentage()

        largest = self.get_largest_pod()
        if self.args.debug:
            print "Largest memory pod: {}".format(largest)

        schedulable = self.how_many_schedulable(largest)

        print "Percentage of memory allocated: {}".format(memory_percentage)
        print "Number of max-size nodes schedulable: {}".format(schedulable)

        self.zagg_sender.add_zabbix_keys({zbx_key_mem_alloc:
                                          int(memory_percentage)})
        self.zagg_sender.add_zabbix_keys({zbx_key_max_pods: schedulable})

if __name__ == '__main__':
    OCC = OpenshiftClusterCapacity()
    OCC.run()
