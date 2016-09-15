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
from openshift_tools.monitoring.zabbix_metric_processor import ZabbixSender, ZabbixMetricProcessor
from openshift_tools.monitoring.metricmanager import MetricManager
from openshift_tools.ansible.simplezabbix import SimpleZabbix

import yaml
import socket
import multiprocessing
import scandir
import random


def get_metric_folders(targetindex, metricpath):
    """Create an array with the shard names from the target's folder
    Args:
        targetindex: the index of the target in the targets array in the config file
        metricpath: the path from the config for the specific zagg target
    Returns: shuffled array of shard folders prefixed with the index of target
        ex: ['0_1a','0_48']
    """
    met_folders = []
    for metfold in scandir.scandir(metricpath):
    # removing the dnd folder from the list of shards, we don't want to process those
        if metfold.name != 'dnd':
            combined = '{0}_{1}'.format(targetindex, metfold.name)
            met_folders.append(combined)
    random.shuffle(met_folders)
    return met_folders

def process_heartbeats(datapack):
    """Send heartbeats to the target

    Args:
        target: the config file portion for this specific target.

    Returns: None
    """
    indexoftarget, shardfolder = datapack.split('_')
    target = CONFIG['targets'][int(indexoftarget)]

    mm = MetricManager(target['path'])
    zbxapi = SimpleZabbix(
        url=target['api_url'],
        user=target['api_user'],
        password=target['api_password'],
    )

    zbxsender = ZabbixSender(target['trapper_server'], target['trapper_port'])

    hostname = socket.gethostname()
    zmp = ZabbixMetricProcessor(mm, zbxapi, zbxsender, hostname, verbose=True)
    zmp.process_hb_metrics(shardfolder)
    return []

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

    for idx, zaggtarget in enumerate(TARGETS):
        logger.info("Sending heartbeats to target [%s]", zaggtarget['name'])
        metrics_folders = get_metric_folders(idx, zaggtarget['path'])

        # We only process heartbeats directly against zabbix targets
        if zaggtarget['type'] == 'zabbix':
            errors = pool.map(process_heartbeats, metrics_folders)
            # TODO: add zabbix item and trigger for tracking the number of errors
            err_count = 0
            for err in errors:
                if len(err) > 0:
                    err_count += len(err)
            if err_count > 0:
                logger.error('Results: %s errors occurred.', err_count)
        else:
            logger.error("Error: Target Type Not Supported: %s", zaggtarget['type'])
            # TODO: add zabbix item and trigger for tracking this failure
