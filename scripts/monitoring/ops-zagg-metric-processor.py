#!/usr/bin/env python2
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

"""This is a script the processes zagg metrics.
"""

from openshift_tools.monitoring.zabbix_metric_processor import ZabbixSender, ZabbixMetricProcessor
from openshift_tools.monitoring.metricmanager import MetricManager
from openshift_tools.ansible.simplezabbix import SimpleZabbix

from openshift_tools.monitoring.zagg_metric_processor import ZaggMetricProcessor
from openshift_tools.monitoring.zagg_common import ZaggConnection
from openshift_tools.monitoring.zagg_client import ZaggClient

import yaml
import socket

class ZaggProcessor(object):
    """Processes all targets found in /etc/openshift_tools/zagg_server.yaml
    """

    def __init__(self, config_file):
        """Constructs the object

        Args:
            config_file: path to the config file on disk
        """

        self.config = yaml.load(file(config_file))

    def run(self):
        """Runs through each defined target in the config file and processes it

        Args: None
        Returns: None
        """
        for target in self.config['targets']:
            print
            print "Sending metrics to target [%s]" % target['name']
            print
            if target['type'] == 'zabbix':
                errors = self.process_zabbix(target)
                # TODO: add zabbix item and trigger for tracking the number of errors
                print
                print "Results: %s errors occurred." % len(errors)
                if errors:
                    print errors
            elif target['type'] == 'zagg':
                # TODO: add error handling for process_zagg like process_zabbix
                self.process_zagg(target)
            else:
                print "Error: Target Type Not Supported: %s" % target['type']
                # TODO: add zabbix item and trigger for tracking this failure

    @staticmethod
    def process_zabbix(target):
        """Process a Zabbix target

        Args:
            target: the config file portion for this specific target.

        Returns: None
        """

        mm = MetricManager(target['path'])
        zbxapi = SimpleZabbix(
            url=target['api_url'],
            user=target['api_user'],
            password=target['api_password'],
        )

        zbxsender = ZabbixSender(target['trapper_server'], target['trapper_port'])

        hostname = socket.gethostname()
        zmp = ZabbixMetricProcessor(mm, zbxapi, zbxsender, hostname, verbose=True)
        return zmp.process_zbx_metrics()

    @staticmethod
    def process_zagg(target):
        """Process a Zagg target

        Args:
            target: the config file portion for this specific target.

        Returns: None
        """

        verify = target.get('ssl_verify', False)

        if isinstance(verify, str):
            verify = (verify == 'True')

        mm = MetricManager(target['path'])
        zagg_conn = ZaggConnection(url=target['url'],
                                   user=target['user'],
                                   password=target['password'],
                                   ssl_verify=verify,
                                  )
        zc = ZaggClient(zagg_conn)

        zmp = ZaggMetricProcessor(mm, zc)
        zmp.process_metrics()

if __name__ == "__main__":
    ZaggProcessor('/etc/openshift_tools/zagg_server.yaml').run()
