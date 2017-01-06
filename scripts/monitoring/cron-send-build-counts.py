#!/usr/bin/env python
""" Build status check for v3 """

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import argparse
import time

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ocutil = OCUtil()

valid_build_states = ["cancelled", "complete", "new", "error", "failed"]

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

    parser = argparse.ArgumentParser(description='OpenShift build status counts')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    return parser.parse_args()

def send_metrics(builds):
    """ send data to MetricSender"""
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    for build_state, count in builds.items():
        logger.debug({'openshift.build_state.%s' % build_state : count})
        ms.add_metric({'openshift.build_state.%s' % build_state : count})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def count_builds():
    """ count build types """

    build_counts = {}
    count_build_time = time.time()

    for build_state in valid_build_states:
        build_counts["%s" % build_state] = 0

    get_builds = "get builds --all-namespaces -o jsonpath='{range .items[*]}{.status.phase}{\"\\n\"}{end}'"
    builds_list = runOCcmd(get_builds).split()
    logger.debug(builds_list)

    for build_item in builds_yaml["items"]:
        build_state = build_item["status"]["phase"].lower()
        logger.debug(build_state)
        if build_state in valid_build_states:
            build_counts["%s" % build_state] += 1

    logger.info(build_counts)
    logger.info("Count generated in %s seconds", str(time.time() - count_build_time))

    return build_counts

def main():
    """ get count of build types, send results """

    logger.debug("main()")

    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        builds = count_builds()

    except Exception as e:
        logger.exception("error during test()")
        exception = e

    send_metrics(builds)

if __name__ == "__main__":
    main()
