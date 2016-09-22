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
#pylint: disable=invalid-name, import-error

"""This is a script the processes heartbeat metrics
"""
import logging
from logging.handlers import RotatingFileHandler
import socket
import multiprocessing
import yaml

from openshift_tools.monitoring.zabbix_metric_processor import ZabbixSender, ZabbixMetricProcessor
from openshift_tools.monitoring.metricmanager import MetricManager
from openshift_tools.ansible.simplezabbix import SimpleZabbix

def process_heartbeats(target):
    """Send heartbeats to the target

    Args:
        target: the config file portion for this specific target.

    Returns: None
    """
    mm = MetricManager(target['name'])
    zbxapi = SimpleZabbix(
        url=target['api_url'],
        user=target['api_user'],
        password=target['api_password'],
    )

    zbxsender = ZabbixSender(target['trapper_server'], target['trapper_port'])

    hostname = socket.gethostname()
    zmp = ZabbixMetricProcessor(mm, zbxapi, zbxsender, hostname, verbose=True)
    zmp.process_hb_metrics()
    return []

def process_targets(target):
    ''' process the targets based on their type'''
    logger.info("Sending heartbeats to target [%s]", target['name'])
    # We only process heartbeats directly against zabbix targets
    if target['type'] == 'zabbix':
        errors = process_heartbeats(target)
        if errors > 0:
            logger.error('Results: %s errors occurred.', len(errors))
    else:
        logger.error("Error: Target Type Not Supported: %s", target['type'])
        # TODO: add zabbix item and trigger for tracking this failure


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    logFile = '/var/log/ops-zagg-heartbeat-processor.log'

    logRFH = RotatingFileHandler(logFile, mode='a', maxBytes=2*1024*1024, backupCount=5, delay=0)
    logRFH.setFormatter(logFormatter)
    logRFH.setLevel(logging.INFO)
    logger.addHandler(logRFH)

    logger.info('Starting ops-zagg-heartbeat-processor...')

    CONFIG = yaml.load(file('/etc/openshift_tools/zagg_server.yaml'))
    pool = multiprocessing.Pool()
    TARGETS = CONFIG['targets']

    pool.map(process_targets, TARGETS)
