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

from openshift_tools.monitoring.metricmanager import MetricManager
from openshift_tools.monitoring.zabbix_metric_processor import ZabbixSender, ZabbixMetricProcessor
from openshift_tools.ansible.simplezabbix import SimpleZabbix

if __name__ == "__main__":
    mm = MetricManager('/tmp/metrics')
    zbxapi = SimpleZabbix(
        url='http://localhost/zabbix/api_jsonrpc.php',
        user='Admin',
        password='zabbix',
    )

    zbxsender = ZabbixSender('localhost', 10051)

    mp = ZabbixMetricProcessor(mm, zbxapi, zbxsender)
    mp.process_metrics()
