#!/usr/bin/env python
''' OpenShift v3 Monitoring '''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

# We just want to see any exception that happens
# don't want the script to die under any cicumstances
# script must try to clean itself up
# pylint: disable=broad-except
# pylint: disable=bare-except

import time
import argparse
import datetime

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
# pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.zagg_sender import ZaggSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='OpenShift Monitoring Project Termination Stats')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    return parser.parse_args()

def send_zagg_data(keep_time):
    ''' send data to Zagg'''
    logger.debug('send_zagg_data()')

    zgs_time = time.time()
    zgs = ZaggSender()
    zgs.add_zabbix_keys({'openshift.master.project.terminating.time': keep_time})

    try:
        zgs.send_metrics()
    except:
        logger.exception('Error sending to Zagg')

    logger.info("Data sent in %s seconds", str(time.time() - zgs_time))

def testProjects(projects, current_time=None,):
    ''' testProjects '''
    logger.info('testProjects() count of projects: %s', len(projects))

    maxDelta = 0
    for project in projects:
        logger.debug(
            "Project: %s Status: %s",
            project['metadata']['name'],
            project['status']['phase']
        )

        if project['status']['phase'] == 'Terminating':
            logger.debug(
                'project[\'metadata\'][\'deletionTimestamp\'] %s',
                project['metadata']['deletionTimestamp']
            )

            projectDeletionTimestamp = project['metadata']['deletionTimestamp']

            timeDelta = current_time - projectDeletionTimestamp
            logger.debug('Project in Terminating status for %s', timeDelta.seconds)

            if current_time > projectDeletionTimestamp:
                maxDelta = max(maxDelta, timeDelta.seconds)
            else:
                logger.warning('current_time <= projectDeletionTimestamp')

            logger.debug('%s', maxDelta)

    return maxDelta

def main():
    ''' main() '''
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting")

    # TODO: include this in library
    projects_info = OCUtil()._run_cmd("oc get projects -o yaml")

    maxDelta = testProjects(
        projects_info['items'],
        current_time=datetime.datetime.now(),
    )

    send_zagg_data(maxDelta)
    logger.info('Oldest Terminating project: %s seconds', maxDelta)

if __name__ == "__main__":
    main()
