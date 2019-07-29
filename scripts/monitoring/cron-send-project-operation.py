#!/usr/bin/env python
""" project creation and deletion check for v3 """

# We just want to see any exception that happens
# don't want the script to die under any cicumstances
# script must try to clean itself up
# pylint: disable=broad-except

# pylint: disable=invalid-name
# pylint: disable=import-error
import argparse
import time

import logging
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ocutil = OCUtil()

commandDelay = 10 # seconds

def runOCcmd(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    oc_time = time.time()
    oc_result = ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - oc_time))
    return oc_result

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='OpenShift project creation and deletion test')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--namespace', default="ops-project-operation-check",
                        help='namespace (be careful of using existing namespaces)')
    return parser.parse_args()

def send_metrics(status_code_create, status_code_delete):
    """ send data to MetricSender"""
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    # 1 means create and delete the project failed
    ms.add_metric({'openshift.master.project.create': status_code_create})
    ms.add_metric({'openshift.master.project.delete': status_code_delete})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def check_project(config):
    """ check create and delete project """
    logger.info('check_project()')
    logger.debug(config)

    project = None

    try:
        project = runOCcmd("get project {}".format(config.namespace))
        logger.debug(project)
    except Exception:
        pass # don't want exception if project not found
    if project:
        project_exist = 1 # project exists
    else:
        project_exist = 0 # project doest not exists

    return project_exist

def create_project(config):
    " create the project "
    try:
        runOCcmd("new-project {}".format(config.namespace), base_cmd='oc adm')
        time.sleep(commandDelay)
    except Exception:
        logger.exception('error creating new project')

def delete_project(config):
    " delete the project "
    try:
        runOCcmd("delete project {}".format(config.namespace), base_cmd='oc')
        time.sleep(commandDelay)
    except Exception:
        logger.exception('error delete project')

def main():
    """ check the project operation status """
    logger.debug("main()")
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    ocutil.namespace = args.namespace
    project_exists = check_project(args)
    # project does not exists.
    delete_project_code = 0

    # delete the project first if it's already there
    if project_exists == 1:
        # the project already exists, try to delete it first.
        delete_project(args)
        delete_project_code = check_project(args)
        if delete_project_code == 1:
            # 1 means project deletion failed, the project still exists
            # give the deletion second chance. 10 more seconds to check the
            # teminating status project
            delete_project(args)
            delete_project_code = check_project(args)
            if delete_project_code == 1:
                logger.info('project deletion failed in 20s')

    # start the test
    logger.info("project does not exists, going to create it")
    create_project(args)
    create_project_code = check_project(args)
    if create_project_code == 0:
        # 0 means project creation failed, no project was created
        logger.info('project creation failed')
    else:
        # project creation succeed, then delete the project
        delete_project(args)
        delete_project_code = check_project(args)
        if delete_project_code == 1:
            # 1 means project deletion failed, the project still exists
            # give the deletion second chance. 10 more seconds to check the
            # teminating status project
            delete_project(args)
            delete_project_code = check_project(args)
            if delete_project_code == 1:
                logger.info('project deletion failed in 20s')
        else:
            delete_project_code = 0
    #logger.info("{} {}".format(create_project_code, delete_project_code))
    if create_project_code == 1 and delete_project_code == 0:
        logger.info('creation and deletion succeed, no data was sent to zagg')

    send_metrics(create_project_code, delete_project_code)

if __name__ == "__main__":
    main()
