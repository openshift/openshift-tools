#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
"""
Implement a rest client with requests for Openshift API

"""
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
#  Openshift API Notes:
#
#  The Openshift Master API has multiple ways it can authenticate. This client
#  library will currently support certificates (support for tokens and oauth
#  could follow.
#
#  Certificates can be used when sending over the API request.  There are
#  different ways to use this library to pass in the certificates.
#
#  1. Pass in the ca_cert, user_cert, and the user_key.
#
#    ora = OpenshiftRestApi(user_cert='/path/to/user_cert',
#                           user_key='/path/to/user_key',
#                           ca_cert='/path/to/ca_cert')
#
#
#  2. The ca_cert, user_cert, and user_key are included in a kubeconfig file.
#     Pass in a kubeconfig file and the api will extract the necessary certs
#     and use them when making the API call.
#
#    ora = OpenshiftRestApi(kubeconfig='/path/to/user.kubeconfig')
#
#  This library will attempt to use the certs if ca, user_cert, and user_key are
#   passed in.  If not, it will attempt to use the kubeconfig file.
#
#
#   Examples:
#
#   # to initiate and use /etc/openshift/master/admin.kubeconfig file for auth
#   ora = OpenshiftRestApi(kubeconfig='/path/to/user.kubeconfig')
#
#   #To get healthz status in text format:
#
#   healthz_status = ora.text_get('/healthz')
#
#   #To get list of users json format:
#
#   healthz_status = ora.json_get('/api/v1/pods')
#
#  For more on the API, please refer to:
#    https://docs.openshift.com/enterprise/3.0/rest_api/index.html
#
import base64
import requests
import yaml
import tempfile
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class OpenshiftRestApi(object):
    """
    A class to simply Openshift API
    """

    # All args are required
    #pylint: disable=too-many-arguments,too-many-instance-attributes
    def __init__(self,
                 host='https://127.0.0.1',
                 user_cert=None,
                 user_key=None,
                 ca_cert=None,
                 kubeconfig='/etc/openshift/master/admin.kubeconfig',
                 headers=None,
                 verify_ssl=False):

        self.api_host = host
        self.headers = headers
        self.verify_ssl = verify_ssl


        if None in (user_cert, user_key, ca_cert):
            self.kubeconfig = kubeconfig
            self.set_keys_from_kubeconfig()
        else:
            self.ca_cert = ca_cert
            self.user_cert = user_cert
            self.user_cert = user_key


    def set_keys_from_kubeconfig(self):
        """ extract and set certs from the kubeconfg file """

        kubecfg_yml = None
        with open(self.kubeconfig, 'r') as yml:
            kubecfg_yml = yaml.load(yml)

        b64_user_cert = kubecfg_yml['users'][0]['user']['client-certificate-data']
        b64_user_key = kubecfg_yml['users'][0]['user']['client-key-data']
        b64_ca_cert = kubecfg_yml['clusters'][0]['cluster']['certificate-authority-data']

        self.user_cert_file = tempfile.NamedTemporaryFile()
        self.user_cert_file.write(base64.b64decode(b64_user_cert))
        self.user_cert_file.flush()
        self.user_cert = self.user_cert_file.name

        self.user_key_file = tempfile.NamedTemporaryFile()
        self.user_key_file.write(base64.b64decode(b64_user_key))
        self.user_key_file.flush()
        self.user_key = self.user_key_file.name

        self.ca_cert_file = tempfile.NamedTemporaryFile()
        self.ca_cert_file.write(base64.b64decode(b64_ca_cert))
        self.ca_cert_file.flush()
        self.ca_cert = self.ca_cert_file.name

    def get(self, api_path, rtype='json'):
        """ Do API query, return requested type """

        ssl_verify = self.verify_ssl
        if ssl_verify:
            ssl_verify = self.ca_cert
        else:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        response = requests.get(self.api_host + api_path,
                                cert=(self.user_cert, self.user_key),
                                verify=ssl_verify)

        if rtype == 'text':
            return response.text
        return response.json()
