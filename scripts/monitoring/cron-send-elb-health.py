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
# pylint: disable=bare-except

from ConfigParser import SafeConfigParser
import argparse
import re
import urllib2
import boto3
from openshift_tools.monitoring.metric_sender import MetricSender

# number instances behind elb
elb_no_instances = []

# number of unhealthy instances
elb_instances_unhealthy = []

# Comparison for instance state
instance_healthy = "InService"

# Monitoring should only report for ELBs created by service of type LoadBalancer in namespaces which are defined in this regex.
watched_ns_regex = '(^kube-.*|^openshift-.*)'

def parse_args():
    ''' parse the args from the cli '''

    parser = argparse.ArgumentParser(description='ELB status checker')
    parser.add_argument('--clusterid', default="", help='clusterid', required=True)
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

def get_elb_name(lb):
    ''' Get ELB name '''
    return lb['LoadBalancerName']

def filter_by_cluster(elb_tags, cluster_id):
    ''' Find all ELBs for a specific cluster '''

    cluster_elbs = []
    for elb_tag_description in elb_tags['TagDescriptions']:
        for elb_tag in elb_tag_description['Tags']:
            if elb_tag['Key'] == 'kubernetes.io/cluster/' + cluster_id:
                cluster_elbs.append(elb_tag_description)

    return cluster_elbs

def filter_monitored_service_elbs(elb_tag_descriptions):
    ''' Filter elbs created by service of type LoadBalancer not in watched namespaces '''

    elbs = []
    for elb_tag_description in elb_tag_descriptions:
        ignore_elb = False
        for elb_tag in elb_tag_description['Tags']:
            # ELBs created by service of type LoadBalancer have a tag where the value is <namespace/service-name>
            # If an elb is created by service of type LoadBalancer but not in a watched namespace, ignore
            if elb_tag['Key'] == 'kubernetes.io/service-name' and not re.match(watched_ns_regex, elb_tag['Value']):
                ignore_elb = True
                break

        if not ignore_elb:
            elbs.append(elb_tag_description)

    return elbs

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
    for i, item in enumerate(elbs_discovered):
        elb_health_checks_raw = client.describe_instance_health(
            LoadBalancerName=item
        )

        # Get https response
        elb_response_http = elb_health_checks_raw['ResponseMetadata']['HTTPStatusCode']

        # Get instance health/state
        elb_instance_response_states = elb_health_checks_raw['InstanceStates']

        # Check count of instances behind each ELB. Alert on 0 count.
        elb_instance_count(elb_instance_response_states, elbs_discovered[i])

        elb_name = elbs_discovered[i]
        # Iterate through each instances health/state behind the ELB
        for elb_instance_response_state in elb_instance_response_states:
            elb_instance_name = elb_instance_response_state['InstanceId']
            elb_instance_state = elb_instance_response_state['State']

            # Check http response
            if elb_response_http != 200:
                print "A potential error occurred. HTTP Response: %s" % elb_response_http

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

    # Call all available loadbalancers in the AWS account and store blob result in elb_descriptions
    elb_descriptions = client.describe_load_balancers()
    elb_names = map(get_elb_name, elb_descriptions['LoadBalancerDescriptions'])

    # Get a list of available ELBs for a cluster
    elb_tags = client.describe_tags(LoadBalancerNames=elb_names)
    cluster_elbs = filter_by_cluster(elb_tags, args.clusterid)

    # Filter any ELBs created by service of type LoadBalancer that is not in our watched namespaces
    monitored_elbs = filter_monitored_service_elbs(cluster_elbs)
    monitored_elb_names = map(get_elb_name, monitored_elbs)

    # Perform health check of each instance available behind each ELB
    elb_health_check(client, monitored_elb_names)

    ### Metric Checks
    if len(elb_no_instances) != 0:
        for _, elb in enumerate(elb_no_instances):
            elb_instances_unhealthy.append(elb)
            print "ELB: %s has no instances behind it. Please investigate." % elb

    ### Unhealthy count check
    elb_instances_unhealthy_metric = len(elb_instances_unhealthy)
    if elb_instances_unhealthy_metric != 0:
        for _, unhealthy in enumerate(elb_instances_unhealthy):
            print unhealthy

#    ''' Now that we know if this instance is missing, feed zabbix '''
    mts = MetricSender(verbose=args.verbose, debug=args.debug)
    mts.add_metric({'openshift.aws.elb.health' : elb_instances_unhealthy_metric})
    mts.send_metrics()

if __name__ == '__main__':
    main()
