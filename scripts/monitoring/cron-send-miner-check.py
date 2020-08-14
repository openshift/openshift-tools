#!/usr/bin/env python
'''
  Send OpenShift Pro Online miner program checks to Zagg
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

# pylint: disable=wrong-import-position
# pylint: disable=broad-except
# pylint: disable=line-too-long

import argparse
import logging
import time
import StringIO
import re
# pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

ocutil = OCUtil()

def runOCcmd(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    oc_time = time.time()
    oc_result = ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )
    logger.debug("oc command took %s seconds", str(time.time() - oc_time))
    return oc_result

def parse_args():
    """ parse the args from the cli """
    parser = argparse.ArgumentParser(description='OpenShift pro online miner check tool')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='increase output verbosity')
    parser.add_argument('-l', '--list', nargs='+', help='A list of pod name for the miner program', required=True)
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    return args

def send_metrics(key, result):
    """ send data to MetricSender """
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    ms.add_metric({key : result})
    logger.debug({key : result})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def check_miner_programs(pods):
    """ check if the miner pods running on the cluster """
    logger.info('Check the miner pods with name: %s', pods)

    miner_list = pods
    pod_list = StringIO.StringIO(runOCcmd("get pod --all-namespaces -o custom-columns=NAME:.metadata.name"))
    miner_count = 0
    miner_pod = []
    for line in pod_list.readlines():
        for name in miner_list:
            if re.search(name, line):
                miner_count += 1
                miner_pod.append(line.rstrip())

    logger.info("Number of miner pods are running on the cluster: %s", miner_count)

    if miner_count != 0:
        logger.debug("A list of miner pods: %s", miner_pod)
    # tolerant if the pod number less than 20
    if miner_count > 20:
        logger.debug("There are more than 20 miner pods running on the cluster")
        return 1
    return 0

def main():
    """ run the monitoring check """
    args = parse_args()

    miner_status = check_miner_programs(args.list)

    miner_program_key = 'openshift.pro.online.miner.abuse'
    miner_program_result = miner_status

    # send metrics to Zabbix
    send_metrics(miner_program_key, miner_program_result)

if __name__ == '__main__':
    main()
