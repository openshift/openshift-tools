#!/usr/bin/env python
'''
  Send OpenShift dedicated cluster secret cert expiration checks to Zagg
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

# pylint: disable=wrong-import-position
# pylint: disable=broad-except
# pylint: disable=line-too-long

# pylint: disable=import-error
import argparse
import logging
import datetime
import time
import base64
import subprocess
from cryptography import x509
from cryptography.hazmat.backends import default_backend
# pylint: disable=import-error
from openshift_tools.monitoring.ocutil import OCUtil
from openshift_tools.monitoring.metric_sender import MetricSender

logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

ocutil = OCUtil()

def runOCcmd(cmd, base_cmd='oc'):
    ''' log commands through ocutil '''
    logger.info(base_cmd + " " + cmd)
    oc_time = time.time()
    oc_result = ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )
    logger.debug("oc command took %s seconds", str(time.time() - oc_time))
    return oc_result

def parse_args():
    ''' parse the args from the cli '''
    parser = argparse.ArgumentParser(description='OpenShift cert expiration from secret')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='increase output verbosity')
    parser.add_argument('-n', '--namespace', default='logging', help='The target namespace for the checks')
    parser.add_argument('-s', '--secret', default='logging-elasticsearch', help='The target secret for the checks')
    parser.add_argument('-d', '--data', default='admin-cert', help='The target secret for the checks')
    parser.add_argument('-z', '--zabbixkey', default='openshift.es.jks.cert.expiry', help='The zabbix key for the check')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    return args

def send_metrics(key, result):
    ''' send data to MetricSender '''
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    ms.add_metric({key : result})
    logger.debug({key : result})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def get_secret(secret_name, data_name, namespace):
    ''' get and decode the targeted secret data for check '''

    # get the specified data of the secret
    secret_data = runOCcmd("get secret {} -n {} --template \'{{{{index .data \"{}\"}}}}\'".format(secret_name, namespace, data_name))

    # decode the data via base64
    decoded_data = base64.b64decode(secret_data)

    return decoded_data

def parse_cert_validate_date(decoded_data):
    ''' get the expire date of the cert '''

    # load the cert via x509
    cert = x509.load_pem_x509_certificate(decoded_data, default_backend())

    return cert.not_valid_after

def check_cert_expiry(date):
    ''' check the cert expiry status '''
    logger.info("Compare the cert expiry date and currect date")

    time_now = datetime.datetime.now()
    cert_expires_time = date

    # send status to zagg if the cert will be expired in 15 days
    if cert_expires_time - time_now < datetime.timedelta(days=15):
        logger.warning("The cert is going to be expired in less than 15 days.")
        return 1
    logger.debug("Cert will be expired in %s", str(cert_expires_time-time_now))
    return 0

def main():
    ''' run the monitoring check '''
    args = parse_args()
    zabbix_key = args.zabbixkey

    try:
        decoded_secret = get_secret(args.secret, args.data, args.namespace)
        expire_date = parse_cert_validate_date(decoded_secret)
        zabbix_result = check_cert_expiry(expire_date)
    except (subprocess.CalledProcessError, TypeError, NameError):
        logger.error("Incorrect parameters!")
        raise SystemExit

    # send metrics to Zabbix
    send_metrics(zabbix_key, zabbix_result)

if __name__ == '__main__':
    main()
