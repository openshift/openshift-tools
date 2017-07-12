#!/usr/bin/env python

""" Check aws instance health """

#pylint: disable=invalid-name
#pylint: disable=line-too-long
#pylint: disable=wrong-import-position

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

import argparse
import os
import time

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender
from openshift_tools.cloud.aws.base import Base

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='AWS instance health')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level, specify multiple')
    parser.add_argument('--aws-creds-profile', required=False, help='The AWS credentials profile to use.')
    return parser.parse_args()

def send_metrics(problems):
    """ send data to MetricSender"""
    logger.debug("send_metrics(problems)")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    ms.add_metric({'aws.ec2.instance.instance_status': problems['InstanceStatus']})
    ms.add_metric({'aws.ec2.instance.system_status': problems['SystemStatus']})
    ms.add_metric({'aws.ec2.instance.events': problems['Events']})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def getInstanceStatusesByRegion(region):
    """ getInstancesByRegion(region) """
    logger.debug("getInstanceStatusesByRegion(region): %s", region)
    region = Base(region, verbose=True)
    return region.ec2.get_all_instance_status()

def testInstance(region=None, instance=None, problems=None):
    """ review status and count problems """

    problems['CountAllInstances'] = problems['CountAllInstances'] + 1

    displayId = region.name + ":" + instance.id

    logger.info("%s %s %s", displayId, "InstanceStatus", instance.instance_status)
    if not instance.instance_status.status == "ok":
        logger.warn("%s %s %s", displayId, "InstanceStatus", instance.instance_status)
        problems['InstanceStatus'] = problems['InstanceStatus'] + 1

    logger.info("%s %s %s", displayId, "SystemStatus", instance.system_status)
    if not instance.system_status.status == "ok":
        logger.warn("%s %s %s", displayId, "SystemStatus", instance.system_status)
        problems['SystemStatus'] = problems['SystemStatus'] + 1

    if instance.events:
        for event in instance.events:
            logger.warn("%s %s %s", displayId, "Events", event.description)
            if event.description.startswith("[Completed]"):
                continue
            problems['Events'] = problems['Events'] + 1
    else:
        logger.info("%s %s %s", displayId, "Events", "OK")

    return problems

def main():
    """ main() """
    logger.debug("main()")

    args = parse_args()

    if args.verbose > 0:
        logger.setLevel(logging.INFO)
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)

    if args.aws_creds_profile:
        os.environ['AWS_PROFILE'] = args.aws_creds_profile

    # get regions
    regions = Base.get_supported_regions()
    logger.debug("regions: %s", regions)

    problems = {
        'CountAllInstances' : 0, # count all instances, including without problems
        'InstanceStatus': 0,
        'SystemStatus': 0,
        'Events' : 0,
    }

    for region in regions:

        instances = getInstanceStatusesByRegion(region.name)
        logger.debug("instances: %s", instances)

        for instance in instances:
            problems = testInstance(region=region, instance=instance, problems=problems)

    logger.warn("Problems: %s", problems)
    send_metrics(problems)

if __name__ == "__main__":
    main()
