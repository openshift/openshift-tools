#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
  Collect information about node within ELB
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

from ConfigParser import SafeConfigParser
from openshift_tools.monitoring.zagg_sender import ZaggSender
import argparse
import urllib2
import yaml
import boto.ec2.elb
import boto.utils

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
    
    aws_access_key = parser.get('elb_monitor','aws_access_key_id')
    aws_secret_key = parser.get('elb_monitor','aws_secret_access_key')

    return [aws_access_key, aws_secret_key]

def get_instance_id():
    ''' Get this instance AWS ID '''

    instance_id = urllib2.urlopen('http://instance-data/latest/meta-data/instance-id').read()

    return instance_id

def get_instance_region():
    ''' Get instances region '''

    instance_zone = urllib2.urlopen('http://instance-data/latest/meta-data/placement/availability-zone').read()
    instance_region = instance_zone[:-1]

    return instance_region

def get_instance_name(zagg_client_file):
    ''' Get this instance name '''

    with open(zagg_client_file, 'r') as f:
        config = yaml.load(f)
    host_name = config["host"]["name"]
    return host_name

def main():
    ''' Gather and examine details about this node within ELBs '''

    AWS_CREDENTIALS = '/root/.aws/credentials'
    ZAGG_CLIENT_CONFIG = '/etc/openshift_tools/zagg_client.yaml'

    args = parse_args()
    zagg_sender = ZaggSender(verbose=args.verbose, debug=args.debug)

    aws_access, aws_secret = get_aws_creds(AWS_CREDENTIALS)
    instance_region = get_instance_region()
    elb = boto.ec2.elb.connect_to_region(instance_region, aws_access_key_id=aws_access, aws_secret_access_key=aws_secret)
    instance_name = get_instance_name(ZAGG_CLIENT_CONFIG)


    ''' Define what instance type this node is, only master/infra are in ELBs '''
    if "master" in instance_name:
        instance_type = "master"
        if args.verbose:
            print "Instance %s type is master." % instance_name
    elif "infra" in instance_name:
        instance_type = "infra"
        if args.verbose:
            print "Instance %s type is infra." % instance_name
    else:
        print "%s is not an infra or master node. Nothing to do."
        exit()


    ''' Fetch the load balancers and make sure this instance is within them '''

    elbs = elb.get_all_load_balancers()
    instance_id = get_instance_id()
    instance_missing = 0

    for i in elbs:
        if instance_type in i.name:
            if not filter(lambda x: x.id == instance_id, i.instances):
                instance_missing = 1
                if args.verbose:
                    print "Instance %s is missing from ELB %s!" % (instance_id, i.name)

    ''' Now that we know if this instance is missing, feed zabbix '''
    zs = ZaggSender(verbose=args.verbose, debug=args.debug)
    zs.add_zabbix_keys({'aws.elb.member_missing' : instance_missing})
    zs.send_metrics()

if __name__ == '__main__':
    main()
