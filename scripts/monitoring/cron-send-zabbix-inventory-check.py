#!/usr/bin/env python
''' collect info of zabbix and compare with info on master  '''

# TODO: change to use arguments for podname, and run once per podname

#pylint: disable=import-error
#pylint: disable=invalid-name
#pylint: disable=broad-except

import argparse
import logging
import json
import urllib2
import sys
from urllib2 import Request, urlopen, URLError, HTTPError
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender
sys.path.insert(0, '/container_setup')
from zabbix_data_sync import *

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logging.getLogger().setLevel(logging.WARN)

class ZabbixInfo(object):
    '''
      this will check the zabbix data and compare it with the real world
    '''
    def __init__(self, args=None, ):
        '''initial for the InfraNodePodStatus'''
        self.args = args
        self.kubeconfig = '/tmp/admin.kubeconfig'
        self.oc = OCUtil(namespace=self.args.namespace, config_file=self.kubeconfig)

    def check_all_hosts(self, zabbix_data_sync_inventory_hosts, clusterid):
        ''' check the situation  '''
        result = 1
        zabbix_data_sync_inventory_hosts_names = []
        for host in zabbix_data_sync_inventory_hosts:
            zabbix_data_sync_inventory_hosts_names.append(host['name'])

        desire_number_cluster = cluster_desired_compute_size + cluster_desired_infra_size + cluster_desired_master_size
        logging.getLogger().info("the requested number of instance is :" + str(desire_number_cluster))
        hosts = self.oc.get_nodes()
        #print hosts
        for host in hosts['items']:
            hostnameincluster = ""
            labels = host['metadata']['labels']
            # Older master nodes may still have a "hostname" metadata label.
            # Otherwise construct the hostname from the provided cluster ID
            # and the "type" and "kubernetes.io/hostname" metadata labels.
            if 'hostname' in labels:
                hostnameincluster = labels['hostname']
            elif 'kubernetes.io/hostname' in labels:
                components = (clusterid, labels['type'], labels['kubernetes.io/hostname'])
                hostnameincluster = '-'.join(components)

            if hostnameincluster in zabbix_data_sync_inventory_hosts_names:
                logging.getLogger().info("found host in zabbix :" + str(hostnameincluster))
            else:
                result = 0
                logging.getLogger().info("host not in zabbix:" + str(hostnameincluster))

        if result == 1:
            if len(hosts['items']) == desire_number_cluster:
                logging.getLogger().info("currrently cluster have :" + str(len(hosts['items'])))
                logging.getLogger().info("all the node under monitoring and the number is the same as requested:" + str(desire_number_cluster))
            else:
                result = 2
                logging.getLogger().info("cluster node number is different with requested")

        return result

    def send_metrics(self, status):
        """send_metrics"""
        ms = MetricSender(verbose=self.args.verbose)
        ms.add_metric({'openshift.master.zabbix.inventory.status': status})
        ms.send_metrics()

def parse_args():
    """ parse the args from the cli """
    logging.getLogger().debug("parse_args()")
    parser = argparse.ArgumentParser(description='AWS instance health')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbosity level, specify multiple')
    parser.add_argument('--clusterid', default="default",
                        help='clusterid')
    parser.add_argument('--namespace', default="default",
                        help='Project namespace')
    args = parser.parse_args()
    if args.verbose > 0:
        logging.getLogger().setLevel(logging.DEBUG)
    return args

if __name__ == '__main__':
    status = 1
    ZABBIX = ZabbixInfo(args=parse_args(), )
    status = ZABBIX.check_all_hosts(zabbix_data_sync_inventory_hosts, ZABBIX.args.clusterid)
    ZABBIX.send_metrics(status)
