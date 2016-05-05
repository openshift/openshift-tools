#!/usr/bin/env python
'''
  Generate an SSL key + csr, upload CSR to cert authority
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#
#   Copyright 2015 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
# Accepting general Exceptions
#pylint: disable=broad-except
# oso modules won't be available to pylint in Jenkins
#pylint: disable=import-error

import argparse
import json
import requests
import os
import yaml
import base64
from OpenSSL import crypto

class OpenshiftCertificateRequester(object):
    """ Generate ssl key + csr, send csr for signing """

    def __init__(self):
        self.args = None
        self.key = None
        self.req = None
        self.config = None

    def run(self):
        """  Main function """

        self.parse_args()
        self.parse_config()
        self.gen_key()
        self.gen_csr()
        self.digicert_submit_csr()

    def gen_key(self):
        """ Generate an ssl private key """

        if os.path.exists(self.config["keyfile"]):
            print "Key file %s exists, not regenerating." % self.config["keyfile"]
            key = open(self.config["keyfile"], "r").read()
        else:
            key = crypto.PKey()
            key.generate_key(crypto.TYPE_RSA, self.config["keylength"])
            open(self.config["keyfile"], "w").write(
                crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
            f = open(self.config["keyfile"], "w")
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
            f.close()

        self.key = key


    def gen_csr(self):
        """ Generate an ssl cert signing request """

        if os.path.exists(self.config["csrfile"]):
            print "CSR file %s exists, not regenerating." % self.config["csrfile"]
        else:
            req = crypto.X509Req()
            req.get_subject().CN = self.config["node"]
            req.get_subject().countryName = self.config["country"]
            req.get_subject().stateOrProvinceName = self.config["state"]
            req.get_subject().localityName = self.config["locality"]
            req.get_subject().organizationName = self.config["org_name"]
            req.get_subject().organizationalUnitName = self.config["ou"]
            req.set_pubkey(self.key)
            req.sign(self.key, 'sha256')
            f = open(self.config["csrfile"], "w")
            f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, req))
            f.close()

        self.req = open(self.config["csrfile"], "r").read()


    def digicert_submit_csr(self):
        """ Upload ssl cert for signing """

        digicert_csr_json = json.JSONEncoder().encode({
            "common_name": self.config["node"],
            "csr": self.req,
            "validity": self.config["valid_years"],
            "server_type": self.config["server_id"],
            "org_name": self.config["org_name"],
            "org_addr1": self.config["org_addr1"],
            "org_city": self.config["locality"],
            "org_state": self.config["org_state"],
            "org_zip": self.config["org_zip"],
            "org_country": self.config["org_country"],
            "org_contact_firstname": self.config["org_firstname"],
            "org_contact_lastname": self.config["org_lastname"],
            "org_contact_email": self.config["org_email"],
            "org_contact_telephone": self.config["org_tel"],
        })

        authstring = self.args.accountnumber + ":" + self.args.apikey
        authstring = base64.b64encode(authstring)
        content_type = 'application/vnd.digicert.rest-v1+json'
        api_headers = {
            "Authorization": "Basic " + authstring,
            "Content-Type": content_type,
        }

        if self.args.debug:
            import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1
            import logging
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

        url = self.args.digicert_api_url + "enterprise/certificate/ssl"
        response = requests.post(url, headers=api_headers, data=digicert_csr_json)
        if self.args.verbose or self.args.debug:
            print response.text

    def parse_args(self):
        """ parse the args from the cli """

        parser = argparse.ArgumentParser(description='OpenShift Cert Generator')
        parser.add_argument('-f', '--configfile', required=True, help='Config file to read')
        parser.add_argument('-u', '--digicert_api_url', help='API url to access Digicert', \
          default='https://api.digicert.com/')
        parser.add_argument('-a', '--apikey', help='Digicert api key')
        parser.add_argument('-n', '--accountnumber', help='Digicert account number')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')

        self.args = parser.parse_args()

    def parse_config(self):
        """ parse config file for additional info needed to generate the cert """

        configfile = open(self.args.configfile, 'r')
        self.config = yaml.load(configfile)

if __name__ == '__main__':
    OWCR = OpenshiftCertificateRequester()
    OWCR.run()
