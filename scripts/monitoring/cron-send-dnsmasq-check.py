#!/usr/bin/env python
""" Create application check for v3 """

# We just want to see any exception that happens
# don't want the script to die under any cicumstances
# script must try to clean itself up
# pylint: disable=broad-except

# main() function has a lot of setup and error handling
# pylint: disable=too-many-statements

# main() function raises a captured exception if there is one
# pylint: disable=raising-bad-type

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import logging
import time
import argparse
import urllib2
import psutil

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

commandDelay = 5 # seconds
# use parsed arg instead
#testLoopCountMax = 180 # * commandDelay = 15min
testCurlCountMax = 18 # * commandDelay = 1min30s
testNoPodCountMax = 18 # * commandDelay = 1min30s


def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='Check the status of dnsmasq')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--url', default='www.redhat.com', help='site to be checked')
    return parser.parse_args()

def send_metrics(curlresult, service_status):
    """ send data to MetricSender"""

    ms = MetricSender()
    ms.add_metric({'openshift.master.dnsmasq.curl.status': curlresult})
    ms.add_metric({'openshift.master.dnsmasq.service.status': service_status})
    ms.send_metrics()

def curl(ip_addr, port, timeout=30):
    """ Open an http connection to the url and read """
    result = 0
    url = 'http://%s:%s' % (ip_addr, port)
    logger.debug("curl(%s timeout=%ss)", url, timeout)

    try:
        http_code = urllib2.urlopen(url, timeout=timeout).getcode()
        if http_code == 200:
            result = 1
        else:
            result = 0
        return result
    except urllib2.HTTPError, e:
        return e.fp.getcode()
    except Exception as e:
        logger.exception("Unknown error")

    return 0

def get_status_of_service():
    """get the status of service"""
    status_code = 0
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            #print pinfo
            if pinfo['name'] == 'dnsmasq':
                status_code = 1
        except psutil.NoSuchProcess:
            print 'error'
    return status_code

def get_curl_service_result(url_tobe_check):
    "get curl_result and service_status"
    curl_result = curl(url_tobe_check, 80)
    service_status = get_status_of_service()
    return curl_result, service_status

def main():
    """check status of dnsmq and report"""
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    curl_service_result = get_curl_service_result(args.url)
    print curl_service_result
    if curl_service_result[0] + curl_service_result[1] < 2:
        time.sleep(5)
        curl_service_result = get_curl_service_result(args.url)

    curl_result = curl_service_result[0]
    service_status = curl_service_result[1]
    send_metrics(curl_result, service_status)
    logger.debug("curlresult:%s", curl_result)
    logger.debug("service_status:%s", service_status)


if __name__ == "__main__":
    main()
