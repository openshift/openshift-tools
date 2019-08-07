#!/usr/bin/env python
'''
  Send OpenShift dedicated cluster terminating pod checks to Zagg
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

# pylint: disable=wrong-import-position
# pylint: disable=broad-except
# pylint: disable=line-too-long

# pylint: disable=import-error
import argparse
import logging
import datetime
import time
import StringIO
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

ocutil = OCUtil()

def runOCcmd(cmd, base_cmd='oc'):
    ''' log commands through ocutil '''
    logger.info(base_cmd + " " + cmd)
    oc_time = time.time()
    oc_result = ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )
    logger.debug("oc command took %s seconds", str(time.time() - oc_time))
    return oc_result

def runOCcmd_yaml(cmd, base_cmd='oc'):
    ''' log commands through ocutil '''
    logger.info(base_cmd + " " + cmd)
    ocy_time = time.time()
    ocy_result = ocutil.run_user_cmd_yaml(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - ocy_time))
    return ocy_result

def parse_args():
    ''' parse the args from the cli '''
    parser = argparse.ArgumentParser(description='OpenShift long time terminating pod check tool')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='increase output verbosity')
    parser.add_argument('--status', default='Terminating', help='Status of pod to check')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    return args

def send_metrics(key, result):
    ''' send data to MetricSender '''
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    ms.add_metric({key : result})
    logger.debug({key : result})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def get_terminating_pods(status):
    ''' check if there is any terminating status pod on the cluster '''
    logger.info('Check the terminating pods')

    pod_list = StringIO.StringIO(runOCcmd("get pod --all-namespaces"))
    # Get a list of terminating pods with name and namespace value
    terminating_pods = {}
    for line in pod_list:
        fields = line.strip().split()
        if fields[3] == status:
            terminating_pods[fields[1]] = fields[0]

    logger.debug("A list of pods in terminating status %s", terminating_pods)

    return terminating_pods

def check_terminating_pod(pods):
    ''' check how long the terminating pod has been in that situation '''
    logger.info('Check the life of the terminating pods')

    # Get the pod's terminated timestamp and compare with the current time
    # if the time difference greater than 10 minutes
    # we thought the pod is stuck in terminating status for too long time
    time_now = datetime.datetime.now()
    long_time_terminate_pod = []
    if pods:
        for pod, ns in pods.iteritems():
            yaml_result = runOCcmd_yaml("get pod {} -n {}".format(pod, ns))
            try:
                pod_finalizer = yaml_result['metadata']['finalizers']
            except KeyError as e:
                pod_finalizer = None
            status_condition = yaml_result['status']['conditions']
            for item in status_condition:
                if item['type'] == "Ready":
                    time_terminated = item['lastTransitionTime']
            status_life = time_now - time_terminated
            # if the pod has finalizer set, we should consider the terminating status is intentional
            if not pod_finalizer and status_life > datetime.timedelta(minutes=5):
                logger.debug("The pod %s has been in terminating status for %s", pod, status_life)
                long_time_terminate_pod.append(pod.rstrip())

    logger.debug("The following pods are in terminating status for long time: %s", long_time_terminate_pod)

    # Consider we are in problem if we have more than 1 pod in terminating
    # status longer than 5 minutes
    if long_time_terminate_pod:
        return 1
    return 0

def main():
    ''' run the monitoring check '''
    args = parse_args()

    pod_list = get_terminating_pods(args.status)
    terminating_pod_status = check_terminating_pod(pod_list)

    terminating_pod_key = 'openshift.terminating.pod.status'
    terminating_pod_result = terminating_pod_status

    # send metrics to Zabbix
    send_metrics(terminating_pod_key, terminating_pod_result)

if __name__ == '__main__':
    main()
