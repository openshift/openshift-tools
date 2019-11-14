#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Collect health of nodes behind all available ELBs
'''
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
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name
# Disabling the import-errors
# pylint: disable=import-error
# Disabling line too long for one character
# pylint: disable=line-too-long
# pylint: disable=pointless-string-statement
# pylint: disable=deprecated-lambda
# pylint: disable=bad-builtin
# pylint: disable=bare-except

from ConfigParser import SafeConfigParser
import argparse
from openshift_tools.monitoring.metric_sender import MetricSender
import urllib2
import yaml
import boto3

# number instances behind elb
elb_no_instances = []

# number of unhealthy instances
elb_instances_unhealthy = []

# Comparison for instance state
instance_healthy = "InService"

def parse_args():
    ''' parse the args from the cli '''

    parser = argparse.ArgumentParser(description='ELB status checker')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
    return parser.parse_args()

def get_aws_creds(creds_file):
    ''' Get AWS authentication details from .aws/credentials file '''

    parser = SafeConfigParser()
    parser.read(creds_file)

    aws_access_key = parser.get('ops_monitoring', 'aws_access_key_id')
    aws_secret_key = parser.get('ops_monitoring', 'aws_secret_access_key')

    return [aws_access_key, aws_secret_key]

def get_instance_id():
    ''' Get this instance AWS ID '''

    instance_id = urllib2.urlopen('http://instance-data/latest/meta-data/instance-id').read()

    return instance_id

def get_instance_region():
    ''' Get instances region '''

    instance_zone = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read()
    instance_region = instance_zone[:-1]

    return instance_region

def discover_elbs(elb_descriptions):
    ''' Find all ELBs and append to list '''
    elbs_discovered = []
    for elb_desc_count in range(len(elb_descriptions['LoadBalancerDescriptions'])):
            elbs_discovered.append(elb_descriptions['LoadBalancerDescriptions'][elb_desc_count]['LoadBalancerName'])

    return elbs_discovered

def elb_instance_count(elb_instances, elb_name):
    ''' Get count of instances behind ELB '''
    if len(elb_instances) == 0:
        elb_no_instances.append(elb_name)

def elb_instance_health(instance_state, instance_name, elb_name):
    ''' Check health of each instance '''
    if instance_state != instance_healthy:
        unhealthy_detected = {
                "elb": elb_name,
                "instance": instance_name,
                "state": instance_state,
                }
        elb_instances_unhealthy.append(unhealthy_detected)

def elb_health_check(client, elbs_discovered):
    ''' Check health of each node found behind each ELB '''

    # Iterate through raw health checks of each instance behind each ELB
    for i in range(len(elbs_discovered)):
        elb_health_checks_raw = client.describe_instance_health(
                LoadBalancerName=elbs_discovered[i]
                )

        # Get https response
        elb_response_http = elb_health_checks_raw['ResponseMetadata']['HTTPStatusCode']

        # Get instance health/state
        elb_instance_response_states = elb_health_checks_raw['InstanceStates']

        # Check count of instances behind each ELB. Alert on 0 count.
        elb_instance_count(elb_instance_response_states, elbs_discovered[i])

        # Iterate through each instances health/state behind the ELB
        for elb_instance_response_state in elb_instance_response_states:
            elb_name = elbs_discovered[i]
            elb_instance_name = elb_instance_response_state['InstanceId']
            elb_instance_state = elb_instance_response_state['State']

            # Check http response
            if elb_response_http != 200:
                print("A potential error occurred. HTTP Response: %s" % elb_response_http)

            elb_instance_health(elb_instance_state, elb_instance_name, elb_name)

def main():
    ''' Gather and examine details about this node within ELBs '''

    args = parse_args()

    aws_access, aws_secret = get_aws_creds('/root/.aws/credentials')
    instance_region = get_instance_region()

    # Create boto client to access ELB resources
    client = boto3.client(
            'elb',
            aws_access_key_id=aws_access,
            aws_secret_access_key=aws_secret,
            region_name=instance_region
            )

    # Call all available loadbalancers and store blob result in elb_descriptions
    elb_descriptions = client.describe_load_balancers()

    # Get a list of available ELBs
    elbs_discovered=discover_elbs(elb_descriptions)

    # Perform health check of each instance available behind each ELB
    elb_health_check(client, elbs_discovered)

    ### Metric Checks
    if len(elb_no_instances) != 0:
        for elb in range(len(elb_no_instances)):
            elb_instances_unhealthy.append(elb_no_instances[elb])
            print("ELB: %s has no instances behind it. Please investigate." % elb_no_instances[elb])

    ### Unhealthy count check
    elb_instances_unhealthy_metric = len(elb_instances_unhealthy)
    if elb_instances_unhealthy_metric != 0:
        for unhealthy in range(elb_instances_unhealthy_metric):
            print(elb_instances_unhealthy[unhealthy])

#    ''' Now that we know if this instance is missing, feed zabbix '''
    mts = MetricSender(verbose=args.verbose, debug=args.debug)
    mts.add_metric({'openshift.aws.elb.health' : elb_instances_unhealthy_metric})
    mts.send_metrics()

if __name__ == '__main__':
    main()
