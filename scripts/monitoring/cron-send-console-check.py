#!/usr/bin/env python
'''
  Send OpenShift Console checks to Zagg
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

# pylint: disable=wrong-import-position
# pylint: disable=broad-except
# pylint: disable=line-too-long

import argparse
import logging
import time
# pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

ocutil = OCUtil()

def runOCcmd_yaml(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    oc_time = time.time()
    oc_result = ocutil.run_user_cmd_yaml(cmd, base_cmd=base_cmd, )
    logger.debug("oc command took %s seconds", str(time.time() - oc_time))
    return oc_result

def parse_args():
    """ parse the args from the cli """
    parser = argparse.ArgumentParser(description='OpenShift console check tool')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='increase output verbosity')
    parser.add_argument('--deployment', default="webconsole", help='deployment name for the web console service')
    parser.add_argument('--namespace', default="openshift-web-console", help='namespace for the web console service')
    parser.add_argument('--deployment2', default="console", help='deployment name for the admin console service')
    parser.add_argument('--namespace2', default="openshift-console", help='namespace for the admin console service')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    return args

def send_metrics(key, result):
    """ send data to MetricSender """
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    ms.add_metric({key : result})
    logger.debug({key : result})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def check_deployment_replicas(deployment):
    """ check if the running replicas is the same as the expected """
    logger.info('Deployment: %s', deployment)

    try:
        deploy = runOCcmd_yaml("get deployment {}".format(deployment))
        running = deploy['status']['availableReplicas']
        expected = deploy['spec']['replicas']
        logger.info("Deployment of %s: Expected replicas %s | Running replicas %s", deployment, expected, running)
        logger.debug(deploy)

        if running == expected:
        # the running replica matches the expected replica
            logger.info("The running replicas of deployment %s has the same value with expected", deployment)
            return 0
        # the running replica dose not match the expected replica
        return 1
    except KeyError as e:
        logger.error("The specified key cannot be found: %s", e)

def check_web_console_pods(args=None, ):
    """ check the web console pods """
    ocutil.namespace = args.namespace
    logger.info('Namespace: %s', args.namespace)
    return check_deployment_replicas(args.deployment)

def check_admin_console_pods(args=None, ):
    """ check the admin console pods """
    ocutil.namespace = args.namespace2
    logger.info('Namespace: %s', args.namespace2)
    return check_deployment_replicas(args.deployment2)

def main():
    """ run the monitoring check """
    args = parse_args()
    logger.debug("Arguments: %s", args)

    web_console_key = 'openshift.webconsole.pod.availability'
    web_console_result = check_web_console_pods(args=args, )

    admin_console_key = 'openshift.adminconsole.pod.availability'
    admin_console_result = check_admin_console_pods(args=args, )

    # send metrics to Zabbix
    send_metrics(web_console_key, web_console_result)
    send_metrics(admin_console_key, admin_console_result)

if __name__ == '__main__':
    main()
