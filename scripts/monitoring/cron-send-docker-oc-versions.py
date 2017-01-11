#!/usr/bin/python
'''
  Send openshift and docker versions with miq_metric tag to metric_sender

  Example:
  ./cron-send-docker-oc-versions.py -u oc_username -p oc_password
'''
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name,import-error

from docker import AutoVersionClient
import subprocess
import argparse
from openshift_tools.monitoring.metric_sender import MetricSender


def parse_args():
    '''Parse the arguments for this script'''
    parser = argparse.ArgumentParser(description="Tool to send docker and openshift versions")
    parser.add_argument('-d', '--debug', default=False, action="store_true", help="debug mode")
    parser.add_argument('-v', '--verbose', default=False, action="store_true", help="Verbose?")

    args = parser.parse_args()
    return args


def main():
    '''get docker and openshift versions and send to metric sender
    '''

    args = parse_args()
    mts = MetricSender(verbose=args.verbose, debug=args.debug)

    # Get docker version
    cli = AutoVersionClient(base_url='unix://var/run/docker.sock', timeout=120)
    docker_version = cli.version()["Version"]
    mts.add_metric({"docker.version": docker_version}, key_tags={'miq_metric': 'true'})

    # Get openshift version
    try:
        return_value = subprocess.check_output("oc version", stderr=subprocess.STDOUT, shell=True)
        oc_version = return_value.split('\n')[0].split(' ')[1]
        mts.add_metric({"oc.version": oc_version}, key_tags={'miq_metric': 'true'})

    except subprocess.CalledProcessError as error:
        print ("Failed to get openshift version: ", error.output)

if __name__ == '__main__':
    main()
