#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a script that can be used to tag EBS volumes in OpenShift v3.

 This script assume that your AWS credentials are setup in ~/.aws/credentials like this:

  [default]
  aws_access_key_id = xxxx
  aws_secret_access_key = xxxx


 Or that environment variables are setup:

  AWS_ACCESS_KEY_ID=xxxx
  AWS_SECRET_ACCESS_KEY=xxxx

"""
# Ignoring module name
# pylint: disable=invalid-name

import argparse
import os

from openshift_tools.cloud.aws.ebs_snapshotter import SUPPORTED_SCHEDULES, EbsSnapshotter
from openshift_tools.cloud.aws.ebs_util import EbsUtil

TAGGER_SUPPORTED_SCHEDULES = ['never'] + SUPPORTED_SCHEDULES


class TaggerCli(object):
    """ Implements the cli interface to the EBS snapshot tagger. """
    def __init__(self):
        self.args = None
        self.parse_args()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='EBS Volume Tagger')
        parser.add_argument('--master-root-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that master root volumes ' + \
                                 'should be tagged with.')
        parser.add_argument('--node-root-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that node root volumes ' + \
                                 'should be tagged with.')
        parser.add_argument('--docker-storage-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that docker storage ' + \
                                 'volumes should be tagged with.')
        parser.add_argument('--autoprovisioned-pv-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that autoprovisioned pv ' + \
                                 'volumes should be tagged with.')
        parser.add_argument('--manually-provisioned-pv-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that manually provisioned pv ' + \
                                 'volumes should be tagged with.')
        parser.add_argument('--unidentified-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that unidentified ' + \
                                 'volumes should be tagged with.')
        parser.add_argument('--retag-volumes', action='store_true', default=False,
                            help='Retag volumes that already have a snapshot tag. ' + \
                                 'DANGEROUS - Only do this if you know what you\'re doing!')
        parser.add_argument('--aws-creds-profile', required=False,
                            help='The AWS credentials profile to use.')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Say what would have been done, but don\'t actually do it.')

        self.args = parser.parse_args()


    def main(self):
        """ Serves as the entry point for the CLI """
        if self.args.aws_creds_profile:
            os.environ['AWS_PROFILE'] = self.args.aws_creds_profile

        for region in EbsUtil.get_supported_regions():
            print
            print "Region: %s:" % region
            eu = EbsUtil(region.name, verbose=True)
            es = EbsSnapshotter(region.name, verbose=True)

            # filter out the already tagged volumes
            skip_volume_ids = []

            if not self.args.retag_volumes:
                # They don't want us to retag volumes that are already tagged, so
                # add the already tagged volumes to the list of volume IDs to skip.
                skip_volume_ids += es.get_already_tagged_volume_ids()

            vol_ids = eu.get_classified_volume_ids(skip_volume_ids)

            ## Actually create the snapshot tags now
            if self.args.master_root_volumes and vol_ids.master_root:
                print
                print "  Setting master root volume tags:"
                es.create_volume_snapshot_tag(vol_ids.master_root, self.args.master_root_volumes,
                                              prefix="    ", dry_run=self.args.dry_run)

            if self.args.node_root_volumes and vol_ids.node_root:
                print
                print "  Setting node root volume tags:"
                es.create_volume_snapshot_tag(vol_ids.node_root, self.args.node_root_volumes,
                                              prefix="    ", dry_run=self.args.dry_run)

            if self.args.docker_storage_volumes and vol_ids.docker_storage:
                print
                print "  Setting docker storage volume tags:"
                es.create_volume_snapshot_tag(vol_ids.docker_storage, self.args.docker_storage_volumes,
                                              prefix="    ", dry_run=self.args.dry_run)

            if self.args.autoprovisioned_pv_volumes and vol_ids.autoprovisioned_pv:
                print
                print "  Setting autoprovisioned pv volume tags:"
                es.create_volume_snapshot_tag(vol_ids.autoprovisioned_pv,
                                              self.args.autoprovisioned_pv_volumes,
                                              prefix="    ", dry_run=self.args.dry_run)

            if self.args.manually_provisioned_pv_volumes and vol_ids.manually_provisioned_pv:
                print
                print "  Setting manually provisioned pv volume tags:"
                es.create_volume_snapshot_tag(vol_ids.manually_provisioned_pv,
                                              self.args.manually_provisioned_pv_volumes,
                                              prefix="    ", dry_run=self.args.dry_run)

            if self.args.unidentified_volumes and vol_ids.unidentified:
                print
                print "  Setting unidentified volume tags:"
                es.create_volume_snapshot_tag(vol_ids.unidentified, self.args.unidentified_volumes,
                                              prefix="    ", dry_run=self.args.dry_run)


if __name__ == "__main__":
    TaggerCli().main()
