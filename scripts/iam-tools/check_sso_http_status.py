#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

#   Copyright 2016 Red Hat Inc.
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

"""
 This script is used to check the return code from /status.php IDP host and report to Zabbix.
 It will report an issue to Zabbix if any received HTTP status codes != 200.
"""

from __future__ import print_function

import os
import requests
import yaml

# Reason: disable pylint import-error because our modules aren't loaded on jenkins.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender


class CheckStatus(object):
    """ Class to check HTTP status code from IDP host. """


    def __init__(self):
        self.sso_status_code = None


    @staticmethod
    def check_http(host):
        """ Check HTTP status codes returned by the IDP host. """

        url_path = 'https://' + host + '/status.php'

        try:
            check_status = requests.get(url_path, verify=False)
            sso_status_code = check_status.status_code
            return sso_status_code

        except requests.exceptions.RequestException as request_exception:
            print(request_exception)
            return None


    def main(self):
        """ Main function. """

# Reason: disable pylint import-error because urllib3 isn't loaded on jenkins.
# pylint: disable=no-member
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
# pylint: enable=no-member
        zag = ZaggSender()
        yaml_config = {}
        config_path = '/etc/openshift_tools/sso-config.yaml'

        if os.path.isfile(config_path):
            with open(config_path, 'r') as sso_config:
                yaml_config = yaml.load(sso_config)

        checks = {
            "sso.service.not.reachable": yaml_config["idp_host"],
            "sso.container.not.reachable": "127.0.0.1:8443"
        }

        for zabbix_key, host in checks.iteritems():
            key_value = 0
            sso_status = self.check_http(host)

            if sso_status != 200:
                key_value += 1

            zag.add_zabbix_keys({zabbix_key: key_value})
            zag.send_metrics()

        running_check = "sso.monitoring.container.running"
        container_running = 1

        zag.add_zabbix_keys({running_check: container_running})
        zag.send_metrics()


if __name__ == '__main__':
    HTTP_STATUS = CheckStatus()
    HTTP_STATUS.main()
