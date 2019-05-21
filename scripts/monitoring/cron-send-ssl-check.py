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
    parser.add_argument('--add_ca_file', nargs='+', help='add CA certificate for validation', default=[], )
    parser.add_argument('--add_ca_path', nargs='+', help='add CA certificates from path for validation', default=[], )
    parser.add_argument('--skip_check_hostname', action='store_true', default=False,
                        help='skip hostname validation, matching the certificate subject')
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



def get_ssl_certificate_expiry_days(domain_name, args=None, ):
    """get the domain expired date"""
    ssl_port = 443
    #docker-registry.default.svc.cluster.local:5000
    if ":" in domain_name:
        ssl_port = domain_name.split(":")[1]
        domain_name = domain_name.split(":")[0]
    conn = ssl.create_connection((domain_name, ssl_port))
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = not args.skip_check_hostname
    context.load_default_certs()

    for ca_file in args.add_ca_file:
        context.load_verify_locations(cafile=ca_file)
        logger.info("add_ca_file: " + ca_file)

    for ca_path in args.add_ca_path:
        context.load_verify_locations(capath=ca_path)
        logger.info("add_ca_path: " + ca_path)

    sock = context.wrap_socket(conn, server_hostname=domain_name)
    cert = ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)

    notafter = x509.get_notAfter()
    notafter = notafter[0:8]
    now = datetime.datetime.now()
    notafter_t = datetime.datetime.strptime(notafter, '%Y%m%d')
    delta = notafter_t - now
    logger.info("[" + domain_name + "] certificate subject: " + str(x509.get_subject()))
    logger.info("[" + domain_name + "] will expire in: " + str(delta.days) + " days")
    return (delta.days if delta.days >= 0 else 0)

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
    exception = None
    try:
        for url in urls:
            expire_day_left = get_ssl_certificate_expiry_days(url, args=args, )
            if expire_day_small > expire_day_left:
                expire_day_small = expire_day_left
        #return the smallest day on this cluster
    except Exception as e:
        logger.exception("error during check the ssl expired info")
        exception = e
        expire_day_small = 0
    try:
        send_metrics(expire_day_small, zabbixkey, args.verbose)
    except Exception as e:
        logger.exception("error sending zabbix data")
        exception = e
    if exception:
        raise exception

if __name__ == "__main__":
    main()
