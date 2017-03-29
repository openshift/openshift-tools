#!/usr/bin/env python
""" Report the usage of the pv """

# We just want to see any exception that happens
# don't want the script to die under any cicumstances
# script must try to clean itself up
# pylint: disable=broad-except

# main() function has a lot of setup and error handling
# pylint: disable=too-many-statements

# main() function raises a captured exception if there is one
# pylint: disable=raising-bad-type

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import argparse
import datetime
import time
import re

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
#pylint: disable=maybe-no-member
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ocutil = OCUtil()

def runOCcmd(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    return ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )

def runOCcmd_yaml(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    return ocutil.run_user_cmd_yaml(cmd, base_cmd=base_cmd, )

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='OpenShift pv usage ')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    return parser.parse_args()

def send_metrics(usage, capacity, used):
    """ send data to MetricSender"""
    logger.debug("send_metrics()")
    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")
    ms.add_metric({'openshift.master.pv.percent.usage': usage})
    ms.add_metric({'openshift.master.pv.capacity.max': capacity})
    ms.add_metric({'openshift.master.pv.capacity.used': used})
    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def get_dynamic_pod_name():
    """get the max_capacity of the cluster"""
    pods = ocutil.get_pods()
    dynamic_pod_name = ""
    pattern = re.compile(r'online-volume-provisioner-')
    for pod in pods['items']:
        pod_name = pod['metadata']['name']
        match = pattern.search(pod_name)
        #find the dynamic pod name
        if match:
            dynamic_pod_name = pod_name
    return dynamic_pod_name

def get_max_capacity(pod_name):
    """get the env from the dynamic pod """
    env_info = runOCcmd_yaml(" env pod/"+pod_name)

    envs = env_info['spec']['containers']
    max_capacity = 0
    for en in envs[0]['env']:
        if en['name'] == 'MAXIMUM_CLUSTER_CAPACITY':
            max_capacity = en['value']
    return max_capacity

def get_pv_usage():
    """get all the pv used """
    pv_info = runOCcmd_yaml(" get pv")
    total = 0
    for pv in pv_info['items']:
        namespace = pv['spec']['claimRef']['namespace']
        capacity = pv['spec']['capacity']['storage']
        if namespace != "openshift-infra" and namespace != "logging":
            capacity_int = int(capacity.strip('GIgi'))
            total = total + capacity_int
    return total
def get_pv_usage_clusterresourcequota():
    """get all the pv used if the cluster is using the clusterresourcequota"""
    pv_info = runOCcmd_yaml(" get clusterresourcequota/persistent-volume ")
    return pv_info


def convert_to_bytes(data):
    """convert to bytes"""
    (number, unit) = re.search("([0-9]+)([A-Za-z]+)", data.strip()).groups()

    if unit.lower() == 'bi':
        return int(number)
    elif unit.lower() == 'ki':
        return int(number) * 1024
    elif unit.lower() == 'mi':
        return int(number) * 1024 * 1024
    elif unit.lower() == 'gi':
        return int(number) * 1024 * 1024 * 1024

    raise Exception("invalid input data: " + data)

def convert_to_kb(data):
    """convert to kib"""
    return float(convert_to_bytes(data)) / 1024

def convert_to_mb(data):
    """convert to mb"""
    return float(convert_to_kb(data)) / 1024

def convert_to_gb(data):
    """convert to gb"""
    return float(convert_to_mb(data)) / 1024


def main():
    """ report pv usage  """

    logger.info('################################################################################')
    logger.info('  Starting Report pv usage - %s', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    logger.info('################################################################################')
    logger.debug("main()")

    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    ocutil.namespace = "openshift-infra"
    dynamic_pod_name = get_dynamic_pod_name()
    if dynamic_pod_name == "":
        pv_info = get_pv_usage_clusterresourcequota()
        #this may be becuase in new version ,will use the clusterresourcequota
        cluster_capacity_max = pv_info['status']['total']['hard']['requests.storage']
        logger.debug("cluster_capacity_max: %s", cluster_capacity_max)
        pv_used = pv_info['status']['total']['used']['requests.storage']
        usage_pv = (convert_to_bytes(pv_used)*100)/convert_to_bytes(cluster_capacity_max)
        logger.debug("percent of usage of pv: %s", usage_pv)
        logger.debug("datasend to zabbix:")
        logger.debug("datasend to zabbix: max_gb %s", convert_to_gb(cluster_capacity_max))
        logger.debug("datasend to zabbix:pv used: %s", convert_to_gb(pv_used))
        send_metrics(usage_pv, convert_to_gb(cluster_capacity_max), convert_to_gb(pv_used))
    else:
        cluster_capacity_max = get_max_capacity(dynamic_pod_name)
        logger.debug("cluster_capacity_max: %s", cluster_capacity_max)
        pv_used = get_pv_usage()
        logger.debug("cluster_pv_used: %s", pv_used)
        cluster_capacity_max_gb = convert_to_gb(cluster_capacity_max)
        #use int to send the usge of %
        usage_pv = (pv_used*100)/cluster_capacity_max_gb
        logger.debug("percent of usage of pv: %s", usage_pv)
        send_metrics(usage_pv, cluster_capacity_max_gb, pv_used)

if __name__ == "__main__":
    main()

