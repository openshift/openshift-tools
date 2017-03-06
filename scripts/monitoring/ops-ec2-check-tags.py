#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a script that gathers tags from instances and reports the status of the tags to zabbix

  Usage:

 ops-ec2-check-tags.py --aws-creds-profile profile1 --clusterid=testcluster --region=us-east-1

"""
# Ignoring module name
# pylint: disable=invalid-name

import os
import argparse
import requests

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender
# uncomment this for realsie
from openshift_tools.cloud.aws.instance_util import InstanceUtil


CONFIG_LOOP_TAG_KEY = 'config_loop.enabled'

class AWSTagsMonitorCLI(object):
    """ Responsible for parsing cli args and running the snapshotter. """

    def __init__(self):
        """ initialize the class """
        self.args = None
        self.parse_args()

    @staticmethod
    def get_current_az():
        """ Returns the Availability Zone that the instance is in. """
        availability_zone = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone').text

        return availability_zone

    @staticmethod
    def get_current_region():
        """ Returns the region that the instance is in. """

        availability_zone = AWSTagsMonitorCLI.get_current_az()
        region = availability_zone[0:-1]

        return region

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='AWS Tag Checker')
        parser.add_argument('--aws-creds-profile', required=False,
                            help='The AWS credentials profile to use.')
        parser.add_argument('--clusterid', required=False,
                            help='The clusterid of items to check')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Say what would have been done, but don\'t actually do it.')
        parser.add_argument('--region', required=False,
                            help='The clusterid of items to check')

        self.args = parser.parse_args()

    def main(self):
        """ main function """

        if not self.args.region:
            self.args.region = AWSTagsMonitorCLI.get_current_region()

        if self.args.aws_creds_profile:
            os.environ['AWS_PROFILE'] = self.args.aws_creds_profile

        instance_util = InstanceUtil(self.args.region, True)

        if self.args.clusterid:
            instances = instance_util.get_all_instances_as_dict(filters={"tag:clusterid" : self.args.clusterid})
        else:
            instances = instance_util.get_all_instances_as_dict()

        tags = []

        # This will print out a list of instances
        #  and the tags associated with them
        for v in instances.itervalues():
            print v.id + ":"
            for name, value in v.tags.iteritems():
                print "  %s: %s" %(name, value)
            print
            tags.append(v.tags)

        print "Sending results to Zabbix:"
        if self.args.dry_run:
            print "  *** DRY RUN, NO ACTION TAKEN ***"
        else:
            AWSTagsMonitorCLI.report_tags_to_zabbix(tags)

    @staticmethod
    def report_tags_to_zabbix(tags):
        """ Sends the commands exit code to zabbix. """
        mts = MetricSender(verbose=True)

        #######################################################
        # This reports the "config" tag from each instance
        #   If config ~= "true", report 0
        #   If config ~= "false", report 1
        #   If config not found, report 2
        #######################################################
        for tag in tags:
            if 'config' in tag.keys():
                if tag['config'].lower() == "true":
                    config_value = 0
                else:
                    config_value = 1
            else:
                config_value = 2

            mts.add_metric({CONFIG_LOOP_TAG_KEY : config_value}, host=tag['Name'])
        ####################################
        # End of config tag checking
        ####################################

        # Actually send them
        mts.send_metrics()

if __name__ == "__main__":
    AWSTagsMonitorCLI().main()
