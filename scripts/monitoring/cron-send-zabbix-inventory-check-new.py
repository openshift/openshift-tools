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
sys.path.insert(0, '/container_setup')

from urllib2 import Request, urlopen, URLError, HTTPError

from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender
from zabbix_hostinfo import node_number_onzabbix

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

    def get_all_hosts(self):
        ''' get all the hosts  '''
        pods = self.oc.get_nodes()
        logging.getLogger().info("number from master is :"+str(len(pods['items'])))
        return len(pods['items'])

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
    parser.add_argument('--namespace', default="default",
                        help='Project namespace')
    args = parser.parse_args()

    if args.verbose > 0:
        logging.getLogger().setLevel(logging.DEBUG)

    return args

if __name__ == '__main__':
    status = 1
    ZABBIX = ZabbixInfo(args=parse_args(), )
    current_number_cluster = ZABBIX.get_all_hosts()
    real_nodenumber_onzabbix = node_number_onzabbix - 3
    if current_number_cluster == real_nodenumber_onzabbix:
        logging.getLogger().info("number are the same")
    else:
        status = 0
        logging.getLogger().info('something wrong , number is different')
    ZABBIX.send_metrics(status)
