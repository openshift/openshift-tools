#!/usr/bin/env python2

'''
    check docker container grpc error
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name
# pylint: disable=wrong-import-position
# pylint: disable=broad-except

import time
import os
import argparse
import logging
import docker

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

# Jenkins doesn't have our tools which results in import errors
# pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender

ZBX_KEY = "docker.container.grpc"

def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='docker grpc error check')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

    arg = parser.parse_args()
    if arg.verbose:
        logger.setLevel(logging.INFO)

    if arg.debug:
        logger.setLevel(logging.DEBUG)

    return arg

if __name__ == "__main__":
    args = parse_args()
    logger.debug("args: ")
    logger.debug(args)

    metric_sender = MetricSender(verbose=args.verbose, debug=args.debug)

    client = docker.from_env()
    container_id = os.environ['container_uuid']
    grpc_error = 0
    try:
        container = client.containers.get(container_id)
        image = container.image
        logger.info("Create a container and run 'date' cmd using image:")
        logger.info(image)
        run_c_time = time.time()
        output = client.containers.run(image=image, command="date", remove=True)
        logger.debug("command took %s seconds", str(time.time() - run_c_time))
        logger.info("Output: %s", output)
        if 'grpc: the connection is unavailable' in output:
            logger.warn("met grpc error: %s", output)
            grpc_error = 1

    except Exception, e:
        logger.info("Get exception: %s", str(e))
        if 'grpc: the connection is unavailable' in str(e):
            logger.warn("met grpc error: %s", str(e))
            grpc_error = 1

    ms = MetricSender(verbose=args.verbose)
    ms.add_metric({ZBX_KEY: grpc_error})
    ms.send_metrics()
