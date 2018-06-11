#!/usr/bin/env python
""" limitRange status Check for OpenShift V3 """

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

# pylint: disable=wrong-import-position
# pylint: disable=broad-except
# pylint: disable=line-too-long

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
    parser.add_argument('--namespace', default="new-monitoring", help='service namespace')

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

def get_limitrange_info(args=None, ):
    """ Test SAML Pod Status """
    ocutil.namespace = args.namespace
    logger.info('Namespace: %s', args.namespace)

    limitRange = runOCcmd_yaml("get LimitRange ")
    #logger.info('Deployment Config availableReplicas: %s', dc['status']['availableReplicas'])
    logger.info('limitRange number is: %s',len(limitRange['items']))
    if len(limitRange['items']) < 1:
        # means no limitRange in this project
        return 0
    else:
        # means under this project we do have limitRange
        return 1


def main():
    """ limitRange status """
    args = parse_args()
    logger.debug("args: ")
    logger.debug(args)

    result = get_limitrange_info(args=args, )

    #send the value to zabbix
    #this was a dynamic item so we can monitoring many project with the same script
    discovery_key_limitrange = 'project.limitrange.num'
    item_prototype_macro_limitrange = '#OSO_LIMITRANGE'
    item_prototype_key_count = 'openshift.project.limitrange.num'
    
    mts = MetricSender(verbose=args.verbose)
    mts.add_dynamic_metric(discovery_key_limitrange, item_prototype_macro_limitrange, args.namespace)
    mts.add_metric({'openshift.project.limitrange.num['+args.namespace+']': result})
    mts.send_metrics()

if __name__ == "__main__":
    main()

