#!/usr/bin/env python
""" config Pod Check for OpenShift V3 """

# pylint: disable=invalid-name

# pylint: disable=wrong-import-position
# pylint: disable=broad-except
# pylint: disable=line-too-long

import argparse
import time
import sys
import logging
sys.path.insert(0, '/container_setup')
from zabbix_data_sync import *

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error

from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

ocutil = OCUtil()

def runOCcmd(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    oc_time = time.time()
    oc_result = ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - oc_time))
    return oc_result

def runOCcmd_yaml(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    ocy_time = time.time()
    ocy_result = ocutil.run_user_cmd_yaml(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - ocy_time))
    return ocy_result

def parse_args():
    """ parse the args from the cli """
    parser = argparse.ArgumentParser(description='configpod status check ')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbosity level, specify multiple')
    parser.add_argument('--namespace', default="openshift-config", help='service namespace')

    args = parser.parse_args()

    if args.verbose > 0:
        logger.setLevel(logging.INFO)
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)

    return args


def test_configpod_pod(args=None, ):
    """ check if the config pod is in the right number """
    ocutil.namespace = args.namespace
    logger.info('Namespace: %s', args.namespace)

    cluster_desired_configpod_count = cluster_desired_infra_size + cluster_desired_compute_size
    pods = runOCcmd_yaml("get pod ")
    running_pod_count = 0

    for pod in pods['items']:
        if pod['status']['phase'] == 'Running':
            running_pod_count  = running_pod_count + 1
    logger.info('Healthy configpod count is : %s', running_pod_count)
    logger.info('the design number is: %s', cluster_desired_configpod_count )
    if running_pod_count == cluster_desired_configpod_count:
        #running config pod number is the same as compute node
        return 1
    else:
        return 0


def main():
    """ config pod check  """
    args = parse_args()
    logger.debug("args: ")
    logger.debug(args)

    result = test_configpod_pod(args=args, )

    #send the value to zabbix
    mts = MetricSender(verbose=args.verbose)
    mts.add_metric({'openshift.master.configpod.status': result})
    mts.send_metrics()

if __name__ == "__main__":
    main()
