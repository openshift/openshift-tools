#!/usr/bin/env python
""" Node taints check for OpenShift V3 """

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

# pylint: disable=wrong-import-position
# pylint: disable=broad-except
# pylint: disable=line-too-long

import argparse
import time

import logging
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

def runOCcmd_yaml(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    ocy_time = time.time()
    ocy_result = ocutil.run_user_cmd_yaml(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - ocy_time))
    return ocy_result

def parse_args():
    """ parse the args from the cli """
    parser = argparse.ArgumentParser(description='Check all the nodes taints Status')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbosity level, specify multiple')

    args = parser.parse_args()

    if args.verbose > 0:
        logger.setLevel(logging.INFO)

    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)

    return args

def check_taint_status():
    """get all the info of all node """
    result_status = 0
    node_info = runOCcmd_yaml("get node ")
    for item in node_info['items']:
        logger.info("Checking node: %s", item['metadata']['name'])
        if "taints" in item['spec']:
            taints = item['spec']['taints']
            for taint in taints:
                result_status = result_status + 1
                logger.warn("Node: %s, have unexpected taint: %s=%s:%s", item['metadata']['name'], taint['key'], taint['value'], taint['effect'])
    return result_status

def main():
    """ check all the node taints see if any node have problem """
    args = parse_args()
    logger.debug("args: ")
    logger.debug(args)

    taint_status = check_taint_status()

    #send the value to zabbix
    mts = MetricSender(verbose=args.verbose)
    mts.add_metric({'openshift.nodes.taint.status': taint_status})
    mts.send_metrics()

if __name__ == "__main__":
    main()
