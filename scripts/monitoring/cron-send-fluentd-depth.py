#!/usr/bin/env python
"""
  Fluentd queue check for v3
"""

import argparse
import time
import subprocess
import math
from dateutil import parser
from datetime import datetime

from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ocutil = OCUtil()

class OpenshiftFluentdQueueCheck(object):
    def __init__(self):
        """ Initialize OpenshiftFluentdQueueCheck class """
        self.metric_sender = None
        self.oc = None
        self.args = None
        self.fluentd_pods = []

    def parse_args(self):
        """ Parse arguments passed to the script """
        parser = argparse.ArgumentParser(description='OpenShift Fluentd Queue Checker')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose output')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

    def send_metrics(self,oldest_buffer):
        """ Send data to MetricSender """
        logger.debug("send_metrics()")

        ms_time = time.time()
        ms = MetricSender()
        logger.info("Sending data to MetricSender...")

        logger.debug({'openshift.logging.fluentd.queue.oldest' : oldest_buffer})
        ms.add_metric({'openshift.logging.fluentd.queue.oldest' : oldest_buffer})

        ms.send_metrics()
        logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

    def get_pods(self):
        """ Get all pods and filter them in one pass """
        pods = self.oc.get_pods()
        for pod in pods['items']:
            if 'component' in pod['metadata']['labels']:
                # Get Fluentd pods
                if pod['metadata']['labels']['component'] == 'fluentd':
                    self.fluentd_pods.append(pod)

    def check_fluentd_queues(self):
        """ Check oldest buffer file in Fluentd pods """
        # Get timestamps of files in /var/lib/fluentd from each pod
        buffer_list = []
        for pod in self.fluentd_pods:
            pod_name = pod['metadata']['name']
            find_ts = "exec " + pod_name + " -- find /var/lib/fluentd -type f -name \*.log ! -name '*output_ops_tag*' -printf '%T+\n'"
            buffer_ts = self.oc.run_user_cmd(find_ts)
            timestamps = buffer_ts.split("\n")
            timestamps.pop() # Removes empty newline
            timestamps.sort()
            if len(timestamps) > 0:
                buffer_list.append(timestamps[0])
                logger.info("Found files in fluentd queue on " + pod_name + " with timestamp(s): %s", str(timestamps)) 
            else:
                logger.info("No files found in fluentd queue on " + pod_name)

        # Convert timestamps to age in seconds 
        age_list=[]
        for ts in buffer_list:
            if "+" in ts:
                ts = ts.replace("+", " ")
                ts = parser.parse(ts)
                ts = ts.replace(tzinfo=None)
                buffer_age = (datetime.now() - ts).total_seconds()
                age_list.append(buffer_age)
        oldest_age = int(math.ceil(max(age_list or [0])))
        logger.info("Oldest fluentd queue file is %s seconds old.", str(oldest_age))
        return oldest_age

    def get_logging_namespace(self):
        """ Determine which logging namespace is in use """
        # Assume the correct namespace is 'openshift-logging' and fall back to 'logging'
        # if that assumption ends up being wrong.
        oc_client = OCUtil(namespace='openshift-logging', config_file='/tmp/admin.kubeconfig', verbose=self.args.verbose)
        logger.info("Determining which namespace is in use...")
        try:
            oc_client.get_dc('logging-kibana')
            # If the previous call didn't throw an exception, logging is deployed in this namespace.
            logger.info("Using namespace: openshift-logging")
            return 'openshift-logging'
        except subprocess.CalledProcessError:
            logger.info("Using namespace: logging")
            return 'logging'

    def run(self):
        """ Main function that runs the check """
        self.parse_args()
        self.metric_sender = MetricSender(verbose=self.args.verbose, debug=self.args.debug)
        self.oc = OCUtil(namespace=self.get_logging_namespace(), config_file='/tmp/admin.kubeconfig', verbose=self.args.verbose)
        self.get_pods()

        oldest_buffer = self.check_fluentd_queues()
	
        self.send_metrics(oldest_buffer)

if __name__ == '__main__':
    OFQC = OpenshiftFluentdQueueCheck()
    OFQC.run()
