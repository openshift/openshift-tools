#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a script that gathers tags from instances and reports the status of the tags to zabbix

 Usage:

 ops-gcp-check-tags.py --gcp-creds-file /root/.gce/creds.json --region=us-east1 --clusterid=testcluster

"""
# Ignoring module name
# pylint: disable=invalid-name

import json
import argparse
# pylint: disable=import-error
# pylint: disable=no-name-in-module
from openshift_tools.cloud.gcp import instance_util

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender

CONFIG_LOOP_TAG_KEY = 'config_loop.enabled'

class GCPTagsMonitorCLI(object):
    """ Responsible for parsing cli args and running the snapshotter. """

    def __init__(self):
        """ initialize the class """
        self.args = None
        self.parse_args()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='PD Snapshotter')
        parser.add_argument('--gcp-creds-file', required=False,
                            help='The GCP credentials to use.')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Say what would have been done, but don\'t actually do it.')
        parser.add_argument('--region', required=True,
                            help='The clusterid of items to check')
        parser.add_argument('--clusterid', required=False,
                            help='The clusterid of items to check')

        self.args = parser.parse_args()

    def main(self):
        """ main function """

        creds = json.loads(open(self.args.gcp_creds_file).read())
        gcpi = instance_util.InstanceUtil(creds['project_id'],
                                          self.args.region,
                                          self.args.gcp_creds_file,
                                          verbose=True)

        all_instances = gcpi.get_all_instances_as_dict()

        # filter out instances based on clusterid
        if self.args.clusterid:
            filter_dict = {'key': 'clusterid', 'value': self.args.clusterid}
            instances = [i for i in all_instances.values() if filter_dict in i['metadata']['items']]
        # else, just grab all the instances
        else:
            instances = all_instances.values()

        instance_tags = [i['metadata']['items'] for i in instances]

        # Moving the {"key" : "key_value", "value" : "value_value" }
        # to { "key_value" : "value_value"
        new_instance_tags = []
        for i in instance_tags:
            new_tags = {}
            for j in i:
                new_tags[j['key']] = j['value']
            new_instance_tags.append(new_tags)

        print "Sending results to Zabbix:"
        if self.args.dry_run:
            print "  *** DRY RUN, NO ACTION TAKEN ***"
        else:
            GCPTagsMonitorCLI.report_tags_to_zabbix(new_instance_tags)

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

            mts.add_metric({CONFIG_LOOP_TAG_KEY : config_value}, host=tag['name'])
        ####################################
        # End of config tag checking
        ####################################

        # Actually send them
        mts.send_metrics()

if __name__ == "__main__":
    GCPTagsMonitorCLI().main()
