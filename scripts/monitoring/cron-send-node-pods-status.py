#!/usr/bin/env python
""" Check all the customer pods status on every compute node, send status code "1" if all pods on a compute node are not running status """

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
    parser = argparse.ArgumentParser(description='Check all the nodes pods Status')
    parser.add_argument('-s', '--skip_namespaces', nargs='+', help='namespaces exception list that we should avoid to check', required=True)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbosity level, specify multiple')

    args = parser.parse_args()

    if args.verbose > 0:
        logger.setLevel(logging.INFO)

    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)

    return args

def check_node_pods_status(nsList):
    """get all the info of all node """
    result_status = 0
    nsFilter = ""
    for ns in nsList:
        nsFilter += ",metadata.namespace!="+ns
    node_info = runOCcmd_yaml("get node ")
    for item in node_info['items']:
        nodeName = item['metadata']['name']
        logger.info("Checking node: %s", item['metadata']['name'])
        node_not_running_pods = runOCcmd_yaml("get pods --all-namespaces --field-selector='spec.nodeName="+nodeName+",status.phase!=Running"+nsFilter+"'")
        node_pods = runOCcmd_yaml("get pods --all-namespaces --field-selector='spec.nodeName="+nodeName+nsFilter+"'")
        if len(node_not_running_pods['items']) == len(node_pods['items']):
            result_status = 1
            logger.warn("Node: %s, all pods are not running", item['metadata']['name'])
    return result_status

def main():
    """ check all the node pods tatus see if any node have problem """
    args = parse_args()
    logger.debug("args: ")
    logger.debug(args)
    nsList = args.skip_namespaces
    pods_status = check_node_pods_status(nsList)

    #send the value to zabbix
    mts = MetricSender(verbose=args.verbose)
    mts.add_metric({'openshift.nodes.pods.status': pods_status})
    mts.send_metrics()

if __name__ == "__main__":
    main()
