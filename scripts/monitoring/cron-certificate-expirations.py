#!/usr/bin/python
''' script to report on expiration dates (in days) for
    certificate expiration '''

# Reason: disable invalid-name because pylint does not like our naming convention
# pylint: disable=invalid-name

import argparse
import datetime
from dateutil import parser
import OpenSSL.crypto
import os
from stat import S_ISDIR, S_ISREG

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is ins talled.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender


CERT_DISC_KEY = 'disc.certificate.expiration'
CERT_DISC_MACRO = '#OSO_CERT_NAME'

class CertificateReporting(object):
    ''' class with ability to parse through x509 certificates to extract
        and report to zabbix the expiration date assocated with the cert '''

    def __init__(self):
        ''' constructor '''
        self.args = None
        self.current_date = datetime.datetime.today()
        self.parse_args()
        self.zsend = ZaggSender(debug=self.args.debug)

    def dprint(self, msg):
        ''' debug printer '''

        if self.args.debug:
            print msg

    def parse_args(self):
        ''' parse command line args '''
        argparser = argparse.ArgumentParser(description='certificate checker')
        argparser.add_argument('--debug', default=False, action='store_true')
        argparser.add_argument('--cert-list', default="/etc/origin", type=str,
                               help='comma-separated list of dirs/certificates')
        self.args = argparser.parse_args()

    def days_to_expiration(self, cert_file):
        ''' return days to expiration for a certificate '''

        crypto = OpenSSL.crypto

        cert = open(cert_file).read()
        certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        expiration_date_asn1 = certificate.get_notAfter()
        # expiration returned in ASN.1 GENERALIZEDTIME format
        # YYYYMMDDhhmmss with a trailing 'Z'
        expiration_date = parser.parse(expiration_date_asn1).replace(tzinfo=None)

        delta = expiration_date - self.current_date
        return delta.days

    def process_certificates(self):
        ''' check through list of certificates/directories '''

        for cert in self.args.cert_list.split(','):
            if not os.path.exists(cert):
                self.dprint("{} does not exist. skipping.".format(cert))
                continue

            mode = os.stat(cert).st_mode
            if S_ISDIR(mode):
                self.all_certs_in_dir(cert)
            elif S_ISREG(mode):
                days = self.days_to_expiration(cert)
                self.dprint("{} in {} days".format(cert, days))
                self.add_to_zabbix(cert, days)
            else:
                self.dprint("not a file. not a directory. skipping.")

        # now push out all queued up item(s) to zabbix
        self.zsend.send_metrics()

    def add_to_zabbix(self, certificate, days_to_expiration):
        ''' queue up item for submission to zabbix '''

        self.zsend.add_zabbix_dynamic_item(CERT_DISC_KEY, CERT_DISC_MACRO,
                                           [certificate])
        zbx_key = "{}[{}]".format(CERT_DISC_KEY, certificate)
        self.zsend.add_zabbix_keys({zbx_key: days_to_expiration})

    def all_certs_in_dir(self, directory):
        ''' recursively go through all *.crt files in 'directory' '''

        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.crt'):
                    full_path = os.path.join(root, filename)
                    days = self.days_to_expiration(full_path)
                    self.dprint("{} in {} days".format(full_path, days))
                    self.add_to_zabbix(full_path, days)

if __name__ == '__main__':
    CertificateReporting().process_certificates()
