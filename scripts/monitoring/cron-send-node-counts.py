#!/usr/bin/env python
""" Node count check for v3 """

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import argparse
import time
import yaml

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.web.openshift_rest_api import OpenshiftRestApi
from openshift_tools.monitoring.metric_sender import MetricSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ora = OpenshiftRestApi()

valid_node_types = ["master", "infra", "compute"]

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='OpenShift node counts')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    return parser.parse_args()

def send_metrics(expected, actual):    
    """ send data to MetricSender """
    logger.debug("send_metrics()")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    for node_count, count in actual.items():
        logger.debug({'openshift.node.count.actual.%s' % node_count : count})
        ms.add_metric({'openshift.node.count.actual.%s' % node_count : count})

    for node_expected, count in expected.items(): 
        logger.debug({'openshift.node.count.expected.%s' % node_expected : count})
        ms.add_metric({'openshift.node.count.expected.%s' % node_expected : count})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def actual_counts():
    """ count nodes currently running """

    node_counts = {}
    count_node_time = time.time()

    for node_type in valid_node_types:
        node_counts[node_type] = 0
    node_counts["unknown"] = 0

    
    response = ora.get('/api/v1/nodes')
    nodes_list = []
    for node in response["items"]:
        nodes_list.append(node["metadata"]["labels"]["type"])

    logger.debug(nodes_list)

    for node_type in nodes_list:
        node_type = node_type.lower()
        logger.debug(node_type)
        if node_type in valid_node_types:
            node_counts[node_type] += 1
        else:
            node_counts["unknown"] += 1

    node_counts["total"] = len(nodes_list)

    logger.info(node_counts)
    logger.info("Count generated in %s seconds", str(time.time() - count_node_time))

    return node_counts

def expected_counts():
    """ get expected node counts """

    with open('/container_setup/monitoring-config.yml') as stream:
        config_data = yaml.load(stream)

    return config_data['cluster_node_count']

def main():
    """ get count of node types, send results """

    logger.debug("main()")

    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    expected = expected_counts()
    actual = actual_counts()

    send_metrics(expected, actual)

if __name__ == "__main__":
    main()
