#!/usr/bin/env python
""" check ssl cert info"""

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

import argparse
import datetime
import random
import string
import time
import urllib2
import ssl
import socket
import logging
import OpenSSL


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

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='OpenShift public ssl expired info check ')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('-key', default="openshift.master.public.ssl.left", help='zabbix key')
    parser.add_argument('-l', '--list', nargs='+', help='domain that need to check', required=True)
    return parser.parse_args()

def send_metrics(day_left, zabbixkey, verbose):
    """ send data to MetricSender"""
    logger.debug("send_metrics()")
    ms_time = time.time()
    ms = MetricSender(verbose=verbose, debug=verbose)
    logger.info("Send data to MetricSender")
    ms.add_metric({zabbixkey: day_left})
    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))



def get_ssl_certificate_expiry_days(domain_name):
    """get the domain expired date"""
    cert = ssl.get_server_certificate((domain_name, 443))
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)

    notafter = x509.get_notAfter()
    notafter = notafter[0:8]
    now = datetime.datetime.now()
    notafter_t = datetime.datetime.strptime(notafter, '%Y%m%d')
    delta = notafter_t - now
    logger.info("public url [" + domain_name + "] will expire in: " + str(delta.days) + " days")
    return delta.days

def main():
    """ check ssl expired info """

    logger.info('################################################################################')
    logger.info('start check the ssl info on this cluster')
    logger.info('################################################################################')

    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    urls = args.list
    expire_day_small = 10000
    zabbixkey = args.key
    try:
        for url in urls:
            expire_day_left = get_ssl_certificate_expiry_days(url)
            if expire_day_small > expire_day_left:
                expire_day_small = expire_day_left
        #return the smallest day on this cluster
    except Exception as e:
        logger.exception("error during check the ssl expired info")
        exception = e
    try:
        send_metrics(expire_day_small, zabbixkey, args.verbose)
    except Exception as e:
        logger.exception("error sending zabbix data")
        exception = e

if __name__ == "__main__":
    main()
