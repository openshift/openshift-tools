#!/usr/bin/env python
""" Check Persistent Volumes Snapshot Tags """

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
import logging
import time
import re
import os

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
#pylint: disable=maybe-no-member
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender
from openshift_tools.cloud.aws.ebs_util import EbsUtil
from openshift_tools.cloud.aws.ebs_snapshotter import SUPPORTED_SCHEDULES, EbsSnapshotter

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ocutil = OCUtil()
DAILY_SCHEDULE = "daily"

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

    parser = argparse.ArgumentParser(description='Check Volume Snapshots ')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--aws-creds-profile', required=False,
                       help='The AWS credentials profile to use.')
    parser.add_argument('--region', required=True,
                       help='The region that we want to process snapshots in')
    return parser.parse_args()

def send_metrics(status):
    """ send data to MetricSender"""
    logger.debug("send_metrics()")
    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")
    ms.add_metric({'openshift.master.pv.snapshots.tags.status': status})
    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def get_pv_volume_ids():
    """get all the ebs volumes id that used by persistent volume"""
    pv_info = runOCcmd_yaml(" get pv")
    volumes = {}
    for pv in pv_info['items']:
        pv_name = pv['metadata']['name']
        if "awsElasticBlockStore" in pv['spec']:
            volume_id = pv['spec']['awsElasticBlockStore']['volumeID'].split("/")[-1]
            volumes[pv_name] = volume_id
    return volumes

def validate_volume_tag(ebs_snapshotter, volume_id, snapshot_tag):
    volume = ebs_snapshotter.ec2.get_all_volumes(volume_ids=[volume_id])[0]
    if "snapshot" in volume.tags and volume.tags['snapshot'] == snapshot_tag:
        return True
    return False

def main():
    """ report pv usage  """

    logger.info('################################################################################')
    logger.info('  Starting Volume Snapshot Tag Checks - %s', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    logger.info('################################################################################')
    logger.debug("main()")

    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if args.aws_creds_profile:
            os.environ['AWS_PROFILE'] = args.aws_creds_profile

    ebs_snapshotter = EbsSnapshotter(args.region, verbose=True)
    if not ebs_snapshotter.is_region_valid(args.region):
        logger.info("Invalid region")
        sys.exit(1)
    else:
        logger.info("Region: %s:", args.region)
        ebs_util = EbsUtil(args.region, verbose=True)
        ebs_snapshotter = EbsSnapshotter(args.region, verbose=True)

    volumes = get_pv_volume_ids()
    status = 0
    for volume in volumes:
        logger.info('Checking pv: %s, volume ID: %s', volume, volumes[volume])
        has_tag = validate_volume_tag(ebs_snapshotter, volumes[volume], DAILY_SCHEDULE)
        if not has_tag:
            logger.warn('pv :%s has no "snapshot:daily" tags', volume)
            status = status + 1

    send_metrics(status)

if __name__ == "__main__":
    main()
