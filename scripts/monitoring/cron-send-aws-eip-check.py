#!/usr/bin/env python

""" Check aws Elastic IP, whether there are EIP that didn't have instance associated """

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

from openshift_tools.monitoring.metric_sender import MetricSender
from openshift_tools.cloud.aws.base import Base

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='Check whether AWS Elastic IP is associated to instances')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level, specify multiple')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
    parser.add_argument('--aws-creds-profile', required=False, help='The AWS credentials profile to use.')
    return parser.parse_args()

def getEIPByRegion(region):
    """ getEIPByRegion(region) """
    logger.debug("getEIPByRegion(region): %s", region)
    region = Base(region, verbose=True)
    return region.ec2.get_all_addresses()

def main():
    """ main() """
    logger.debug("main()")

    args = parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.verbose:
        logger.setLevel(logging.INFO)

    if args.aws_creds_profile:
        os.environ['AWS_PROFILE'] = args.aws_creds_profile

    ms = MetricSender(verbose=args.verbose, debug=args.debug)
    # get regions
    regions = Base.get_supported_regions()
    logger.debug("Get all regions: %s", regions)

    count = 0
    for region in regions:
        logger.info("Get Elastic IP in region %s", region)
        eips = getEIPByRegion(region.name)
        logger.debug("elastic ips: %s", eips)
        for eip in eips:
            if eip.instance_id is None:
                count += 1
                logger.warn("EIP: %s is not associated to any instance", eip)

    ms_time = time.time()
    logger.info("Send data to MetricSender")

    ms.add_metric({'aws.ec2.eip.status': count})
    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

if __name__ == "__main__":
    main()
