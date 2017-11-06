#!/usr/bin/env python
'''
  Send EBS volumes that are stuck in a transition state
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#
#   Copyright 2017 Red Hat Inc.
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

import argparse
import os.path
import re
from datetime import datetime, timedelta

import yaml

from openshift_tools.cloud.aws.ebs_util import EbsUtil
from openshift_tools.monitoring.metric_sender import MetricSender
from openshift_tools.monitoring.ocutil import OCUtil


STATE_DATA_FILE = "/tmp/ebs_volume_state_data.yaml"

VOLUME_ID_KEY = 'volume_id'
STUCK_AFTER_KEY = 'stuck_after'
ATTACH_STATUS_KEY = 'attach_status'
STATE_KEY = 'state'

STUCK_STATE = 'stuck'
UNSTUCK_STATE = 'unstuck'
TRANSITION_STATE = 'transitioning'

EBS_VOLUME_URI_DISC_KEY = 'disc.aws.ebs'
EBS_VOLUME_URI_DISC_MACRO = '#OSO_EBS_VOLUME_URI'
EBS_VOLUME_ATTACH_STATE_KEY = 'disc.aws.ebs.attach_state'

MONITORING_STUCK_VALUE = 1
MONITORING_UNSTUCK_VALUE = 0



class EBSStuckVolumesCheck(object):
    """
       This class houses a check that looks for EBS volumes that are stuck in a
       transition state (attaching, detaching, busy, etc).
    """

    def __init__(self):
        """ initialize EBSStuckVolumesCheck class """
        self.args = None
        self.vol_state_data = None

        self.parse_args()

        # Make sure we're using the profile they've requested.
        if self.args.aws_creds_profile:
            os.environ['AWS_PROFILE'] = self.args.aws_creds_profile

        self.eu = EbsUtil(self.args.region, verbose=self.args.verbose)
        self.ocutil = OCUtil(verbose=self.args.verbose)
        self.mts = MetricSender(verbose=self.args.verbose)

    def parse_args(self):
        ''' Parse arguments passed to the script '''
        parser = argparse.ArgumentParser(description='OpenShift Cluster Metrics Checker')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose output')
        parser.add_argument('--region', required=True, help='AWS EC2 Region to check')
        parser.add_argument('--stuck-after', default=120, type=int,
                            help='Amount of time in seconds after which the volume is ' + \
                                 'determined to be "stuck".')
        parser.add_argument('--aws-creds-profile', required=False,
                            help='The AWS credentials profile to use.')

        self.args = parser.parse_args()

    @staticmethod
    def read_raw_volume_state_data():
        """ Reads in the raw string the volume state data from disk """
        if not os.path.isfile(STATE_DATA_FILE):
            return ""  # Act like the file is blank

        with open(STATE_DATA_FILE, 'r') as stream:
            return stream.read()

    def load_volume_state_data(self):
        """ Loads the volume state data from disk """
        if os.path.isfile(STATE_DATA_FILE):
            with open(STATE_DATA_FILE, 'r') as stream:
                self.vol_state_data = yaml.load(stream)
        else:
            self.vol_state_data = {}

    def save_volume_state_data(self):
        """ Saves the volume state data to disk """
        with open(STATE_DATA_FILE, 'w') as outfile:
            yaml.dump(self.vol_state_data, outfile, default_flow_style=False, allow_unicode=True)

    def add_new_transitioning_volumes(self, trans_vols):
        """ Adds volumes that we haven't seen before that are in a transitioning state. """
        for vol in trans_vols:
            vol_uri = self.eu.generate_volume_uri(vol)

            if vol_uri not in self.vol_state_data.keys():
                # This is the first time we've seen this volume, add it.
                vol_uri = self.eu.generate_volume_uri(vol)
                self.vol_state_data[vol_uri] = {}
                self.vol_state_data[vol_uri][STUCK_AFTER_KEY] = datetime.now() + \
                    timedelta(seconds=self.args.stuck_after)
                self.vol_state_data[vol_uri][VOLUME_ID_KEY] = str(vol.id)
                self.vol_state_data[vol_uri][STATE_KEY] = TRANSITION_STATE

            self.vol_state_data[vol_uri][ATTACH_STATUS_KEY] = str(vol.attach_data.status)

    def set_stuck_volumes(self):
        """ Sets volumes to state 'stuck' if they've passed their transition state deadline. """
        for item in self.vol_state_data.itervalues():
            # We don't want to set unstuck volumes back to stuck.
            if item[STATE_KEY] != UNSTUCK_STATE:
                if datetime.now() > item[STUCK_AFTER_KEY]:
                    item[STATE_KEY] = STUCK_STATE

    def set_unstuck_volumes(self, trans_vols):
        """
            Change volumes that were in state 'stuck' that are no longer in transition,
            to state 'unstuck'.
        """

        trans_vol_ids = [str(vol.id) for vol in trans_vols]

        for vol_uri, cache_data in self.vol_state_data.iteritems():
            if cache_data[STATE_KEY] == STUCK_STATE and \
               cache_data[VOLUME_ID_KEY] not in trans_vol_ids:
                # This volue was stuck, but isn't any longer
                self.vol_state_data[vol_uri][STATE_KEY] = UNSTUCK_STATE

    def report_stuck_volumes(self):
        """ sends data to monitoring that these volumes are stuck. """
        for vol_uri, cache_data in self.vol_state_data.iteritems():
            if cache_data[STATE_KEY] == STUCK_STATE:
                self.mts.add_dynamic_metric(EBS_VOLUME_URI_DISC_KEY, EBS_VOLUME_URI_DISC_MACRO, [vol_uri])

                item_name = '%s[%s]' % (EBS_VOLUME_ATTACH_STATE_KEY, vol_uri)
                self.mts.add_metric({item_name: MONITORING_STUCK_VALUE})

        # Actually send them
        self.mts.send_metrics()

    def report_unstuck_volumes(self):
        """ sends data to monitoring that these volumes have become unstuck. """
        for vol_uri, cache_data in self.vol_state_data.iteritems():
            if cache_data[STATE_KEY] == UNSTUCK_STATE:
                self.mts.add_dynamic_metric(EBS_VOLUME_URI_DISC_KEY, EBS_VOLUME_URI_DISC_MACRO, [vol_uri])

                item_name = '%s[%s]' % (EBS_VOLUME_ATTACH_STATE_KEY, vol_uri)
                self.mts.add_metric({item_name: MONITORING_UNSTUCK_VALUE})

        # Actually send them
        self.mts.send_metrics()


    def remove_unstuck_volumes_from_state_data(self):
        """ Removes state 'unstuck' volumes from the state data (no longer need to track them) """
        for vol_uri in self.vol_state_data.keys():
            cache_data = self.vol_state_data[vol_uri]
            if cache_data[STATE_KEY] == UNSTUCK_STATE:
                # This volume was stuck, but isn't any longer
                del self.vol_state_data[vol_uri]

    def remove_no_longer_transitioning_volumes(self, trans_vols):
        """ Remove volumes that were transitioning, but are no longer in the trans_vols list """

        trans_vol_ids = [str(vol.id) for vol in trans_vols]

        for vol_uri in self.vol_state_data.keys():
            cache_data = self.vol_state_data[vol_uri]
            if cache_data[STATE_KEY] == TRANSITION_STATE and \
               cache_data[VOLUME_ID_KEY] not in trans_vol_ids:
                # This volume was transitioning, but isn't any longer
                del self.vol_state_data[vol_uri]

    def get_cluster_volumes(self):
        """ Return the cluster's volume list """
        volume_list = self.ocutil.get_pvs()['items']
        just_the_aws_path = [x['spec']['awsElasticBlockStore']['volumeID'] for x in volume_list]

        just_the_volume_ids = [re.sub("^aws://.*/", "", x) for x in just_the_aws_path]

        return just_the_volume_ids

    @staticmethod
    def filter_out_non_cluster_vols(account_vols, cluster_vols):
        """ We have a list of all volumes in the account, return only
            those that are part of this cluster """

        cluster_list = [x for x in account_vols if x.id in cluster_vols]

        return cluster_list

    def run(self):
        """ Run the main logic of this check """

        # Load the state machine data
        self.load_volume_state_data()

        # Get the volumes that are currently in a transitioning state
        full_trans_vols = self.eu.get_trans_attach_status_vols()

        # Get the cluster's list of volumes
        cluster_vols = self.get_cluster_volumes()

        # Remove volumes that aren't part of this cluster
        trans_vols = self.filter_out_non_cluster_vols(full_trans_vols, cluster_vols)

        # Based on that list, weed out the volumes that used to be transitioning,
        # that are no longer in the transitioning volumes list. This means that
        # it was a normal volume transition, probably from attaching to attached
        # or detaching to detached (aka None).
        self.remove_no_longer_transitioning_volumes(trans_vols)

        # Check on the volumes that were in the stuck state that are no longer
        # in the transitioning volumes list. This means that they went from stuck
        # to unstuck. We need to track these so that we can report that they've become
        # unstuck to monitoring.
        self.set_unstuck_volumes(trans_vols)

        # Add any volumes that are transitioning that we haven't seen before to our data
        self.add_new_transitioning_volumes(trans_vols)

        # Change volumes that are still transitioning and have hit their deadline to
        # finish that transition to a state of "stuck"
        self.set_stuck_volumes()

        # Report to monitoring the stuck volumes
        self.report_stuck_volumes()

        # Report to monitoring the volumes that were stuck, but are now unstuck (no
        # longer transitioning)
        self.report_unstuck_volumes()

        # Since the unstuck volumes have been reported, they can safeuly be removed from
        # our tracking now.
        self.remove_unstuck_volumes_from_state_data()

        # Make sure we save state for the next run.
        self.save_volume_state_data()

        self.eu.verbose_print("\nTracking Volumes")
        self.eu.verbose_print("----------------\n")

        # Cat out the state file
        raw_state_file = self.read_raw_volume_state_data()
        self.eu.verbose_print(raw_state_file)



if __name__ == '__main__':
    esvc = EBSStuckVolumesCheck()
    esvc.run()
