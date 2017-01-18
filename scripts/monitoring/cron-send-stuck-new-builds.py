#!/usr/bin/env python
""" Build status check for v3 """

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import argparse
import time
from dateutil import parser
from datetime import datetime

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

def runOCcmd(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    return ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    argparser = argparse.ArgumentParser(description='OpenShift stuck new build count')
    argparser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    argparser.add_argument('-a', '--age', action='store', default=180, type=int,
                           help='How long a build can stay in New state before being considered stuck.')
    return argparser.parse_args()

def send_metrics(stuck_builds):
    """ send data to MetricSender"""
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    logger.debug({'openshift.stuck_new_builds' : stuck_builds})
    ms.add_metric({'openshift.stuck_new_builds' : stuck_builds})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def get_stuck_build_count(age):
    """
        Return a count of the number of builds that have remained
        in New state longer than 'age' seconds.
    """

    count_build_time = time.time()

    # custom columns method - left for future reference
    #get_builds="get builds -o=custom-columns=Phase:.status.phase,TS:.status.startTimestamp --all-namespaces"

    # go template method - shiny!
    get_new_build_timestamps = ("get builds --all-namespaces -o go-template='{{range .items}}"
                                "{{if eq .status.phase \"New\"}}{{.status.startTimestamp}}"
                                "{{print \"\\n\"}}{{end}}{{end}}'")

    all_ts = runOCcmd(get_new_build_timestamps).split()
    #logger.debug(all_ts)
    #epoch = datetime.datetime.utcfromtimestamp(0)
    stuck_build_count = 0

    for ts in all_ts:
        if "Z" in ts:
            ts = parser.parse(ts)
            ts = ts.replace(tzinfo=None)
            #logger.debug(ts)
            build_age = (datetime.now() - ts).total_seconds()
            #build_age = time.time() - ts_as_epoch
            logger.debug("build age: %s ", build_age)
            if build_age > age:
                stuck_build_count += 1

    logger.info("Count generated in %s seconds", str(time.time() - count_build_time))

    return stuck_build_count

def main():
    """ get count of builds stuck in New state, send results """

    logger.debug("main()")

    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    stuck_builds = get_stuck_build_count(args.age)

    send_metrics(stuck_builds)

if __name__ == "__main__":
    main()
