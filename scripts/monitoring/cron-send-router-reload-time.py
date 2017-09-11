#!/usr/bin/env python
""" Test how long it takes the router config to reload """

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import argparse
import time
import logging

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

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

    argparser = argparse.ArgumentParser(description='OpenShift HAProxy reload timer')
    argparser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    return argparser.parse_args()

def send_metrics(reload_time):
    """ send data to MetricSender"""
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    ms.add_metric({'openshift.haproxy.reload_time' : reload_time})
    logger.debug({'openshift.haproxy.reload_time' : reload_time})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def get_router_reload_time():
    """
        Return time in seconds it takes to reload HAProxy config
    """

    reload_proxy = ('rsh -n default dc/router "../reload-haproxy"')
    start_reload_time = time.time()
    reload_proxy_run = runOCcmd(reload_proxy)
    reload_time = time.time() - start_reload_time
    logger.debug(reload_proxy_run)
    logger.info("Proxy reloaded in in %s seconds", reload_time)

    return reload_time

def main():
    """ Measure time to reload haproxy, send results """

    logger.debug("main()")

    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    reload_time = get_router_reload_time()

    send_metrics(reload_time)

if __name__ == "__main__":
    main()
