#!/usr/bin/env python
""" SAML Pod Check for OpenShift V3 """

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

# pylint: disable=wrong-import-position
# pylint: disable=broad-except

import argparse
import time
import urllib2

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error

from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

ocutil = OCUtil()

def runOCcmd(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    oc_time = time.time()
    oc_result = ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - oc_time))
    return oc_result

def runOCcmd_yaml(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    ocy_time = time.time()
    ocy_result = ocutil.run_user_cmd_yaml(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - ocy_time))
    return ocy_result

def parse_args():
    """ parse the args from the cli """
    parser = argparse.ArgumentParser(description='OpenShift app create end-to-end test')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbosity level, specify multiple')
    parser.add_argument('--dc', default="saml-auth", help='deployment config name')
    parser.add_argument('--service', default="saml-auth", help='service name')
    parser.add_argument('--namespace', default="default", help='service namespace')

    args = parser.parse_args()

    if args.verbose > 0:
        logger.setLevel(logging.INFO)
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)

    return args

def gen_test_url(service):
    """ Generate Test URL """
    return "https://%s:%s/logged_out.html" % (
        service['spec']['clusterIP'],
        443
    )

def curl(url):
    """ Test URL, return http code """
    try:
        return urllib2.urlopen(url, timeout=30).getcode()
    except urllib2.HTTPError as e:
        return e.fp.getcode()
    except Exception:
        logger.exception("unknown error")

    return 0

def test_saml_pod(args=None, ):
    """ Test SAML Pod Status """
    ocutil.namespace = args.namespace
    logger.info('Namespace: %s', args.namespace)

    dc = runOCcmd_yaml("get dc {}".format(args.service))
    logger.info('Deployment Config replicas: %s', dc['status']['replicas'])
    logger.info('Deployment Config availableReplicas: %s', dc['status']['availableReplicas'])
    logger.debug(dc)

    if dc['status']['availableReplicas'] < 1:
        # Pod not running
        return 0

    service = runOCcmd_yaml("get service {}".format(args.service))
    logger.info('Service: %s', args.service)
    logger.debug(service)

    url = gen_test_url(service)
    logger.info('Service IP: %s', service['spec']['clusterIP'])
    logger.info('Service URL: %s', url)

    curl_status = curl(url)
    logger.info("HTTP response (curl): %s", curl_status)

    if curl_status == 200:
        # everything is ok
        return 1
    else:
        # we have the pod, but bad http response
        return 2

def main():
    """ SAML Pod Status """
    args = parse_args()
    logger.debug("args: ")
    logger.debug(args)

    result = test_saml_pod(args=args, )

    #send the value to zabbix
    mts = MetricSender(verbose=args.verbose)
    mts.add_metric({'openshift.master.saml.status': result})
    mts.send_metrics()

if __name__ == "__main__":
    main()
