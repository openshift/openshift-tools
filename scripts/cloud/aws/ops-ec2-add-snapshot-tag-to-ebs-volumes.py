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
import sys
import logging
from logging.handlers import RotatingFileHandler

from openshift_tools.cloud.aws.ebs_snapshotter import SUPPORTED_SCHEDULES, EbsSnapshotter
from openshift_tools.cloud.aws.ebs_util import EbsUtil

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logFile = '/var/log/ec2-add-snapshot-tag-to-ebs-volumes.log'

logRFH = RotatingFileHandler(logFile, mode='a', maxBytes=2*1024*1024, backupCount=5, delay=0)
logRFH.setFormatter(logFormatter)
logRFH.setLevel(logging.INFO)
logger.addHandler(logRFH)
logConsole = logging.StreamHandler()
logConsole.setFormatter(logFormatter)
logConsole.setLevel(logging.WARNING)
logger.addHandler(logConsole)


TAGGER_SUPPORTED_SCHEDULES = ['never'] + SUPPORTED_SCHEDULES


ROOT_VOLUME_PURPOSE = "root volume"
DOCKER_VOLUME_PURPOSE = "docker storage volume"
PV_PURPOSE = "customer persistent volume"


class TaggerCli(object):
    """ Implements the cli interface to the EBS snapshot tagger. """
    def __init__(self):
        self.args = None
        self.parse_args()
        if self.args.verbose:
            logConsole.setLevel(logging.INFO)
        if self.args.debug:
            logConsole.setLevel(logging.DEBUG)
        if self.args.skip_boto_logs:
            logging.getLogger('boto').setLevel(logging.WARNING)

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
        parser.add_argument('--set-name-tag', action='store_true', default=False,
                            help='Add the Name tag to volumes of the host where this ' + \
                                 'volume is attached.')
        parser.add_argument('--set-purpose-tag', action='store_true', default=False,
                            help='Add the purpose tag to volumes')
        parser.add_argument('--retag-volumes', action='store_true', default=False,
                            help='Retag volumes that already have a snapshot tag. ' + \
                                 'DANGEROUS - Only do this if you know what you\'re doing!')
        parser.add_argument('--aws-creds-profile', required=False,
                            help='The AWS credentials profile to use.')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Say what would have been done, but don\'t actually do it.')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
        parser.add_argument('--skip-boto-logs', action='store_true', default=False, help='Skip boto logs')
        parser.add_argument('--region', required=True,
                            help='The region that we want to process snapshots in')

        self.args = parser.parse_args()

    def set_master_root_volume_tags(self, master_root_vol_ids, ebs_snapshotter, ebs_util):
        """ Sets tags on master root volumes """
        logger.debug("Setting master root volume tags:")
        ebs_snapshotter.set_volume_snapshot_tag(master_root_vol_ids, self.args.master_root_volumes,
                                                prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_purpose_tag:
            ebs_util.set_volume_purpose_tag(master_root_vol_ids, ROOT_VOLUME_PURPOSE,
                                            prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_name_tag:
            ebs_util.set_volume_name_tag(master_root_vol_ids, prefix="    ", dry_run=self.args.dry_run)

    def set_node_root_volume_tags(self, node_root_vol_ids, ebs_snapshotter, ebs_util):
        """ Sets tags on node root volumes """
        logger.debug("Setting node root volume tags:")
        ebs_snapshotter.set_volume_snapshot_tag(node_root_vol_ids, self.args.node_root_volumes,
                                                prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_purpose_tag:
            ebs_util.set_volume_purpose_tag(node_root_vol_ids, ROOT_VOLUME_PURPOSE,
                                            prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_name_tag:
            ebs_util.set_volume_name_tag(node_root_vol_ids, prefix="    ", dry_run=self.args.dry_run)

    def set_docker_storage_volume_tags(self, docker_storage_vol_ids, ebs_snapshotter, ebs_util):
        """ Sets tags on docker storage volumes """
        logger.debug("Setting docker storage volume tags:")
        ebs_snapshotter.set_volume_snapshot_tag(docker_storage_vol_ids, self.args.docker_storage_volumes,
                                                prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_purpose_tag:
            ebs_util.set_volume_purpose_tag(docker_storage_vol_ids, DOCKER_VOLUME_PURPOSE,
                                            prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_name_tag:
            ebs_util.set_volume_name_tag(docker_storage_vol_ids, prefix="    ", dry_run=self.args.dry_run)

    def set_manually_provisioned_pv_volume_tags(self, manually_provisioned_pv_vol_ids, ebs_snapshotter, ebs_util):
        """ Sets tags on manually provisioned pv volumes """
        logger.debug("Setting manually provisioned pv volume tags:")
        ebs_snapshotter.set_volume_snapshot_tag(manually_provisioned_pv_vol_ids,
                                                self.args.manually_provisioned_pv_volumes,
                                                prefix="    ", dry_run=self.args.dry_run)

        # NOTE: not setting Name tag because PVs don't belong to a specific host.

        if self.args.set_purpose_tag:
            ebs_util.set_volume_purpose_tag(manually_provisioned_pv_vol_ids, PV_PURPOSE,
                                            prefix="    ", dry_run=self.args.dry_run)

    def set_autoprovisioned_pv_volume_tags(self, autoprovisioned_pv_vol_ids, ebs_snapshotter, ebs_util):
        """ Sets tags on autoprovisioned pv volumes """
        logger.debug("Setting autoprovisioned pv volume tags:")
        ebs_snapshotter.set_volume_snapshot_tag(autoprovisioned_pv_vol_ids,
                                                self.args.autoprovisioned_pv_volumes,
                                                prefix="    ", dry_run=self.args.dry_run)

        # NOTE: not setting Name tag because PVs don't belong to a specific host.

        if self.args.set_purpose_tag:
            ebs_util.set_volume_purpose_tag(autoprovisioned_pv_vol_ids, PV_PURPOSE,
                                            prefix="    ", dry_run=self.args.dry_run)

    def set_unidentified_volume_tags(self, unidentified_vol_ids, ebs_snapshotter):
        """ Sets tags on unidentified pv volumes """
        logger.debug("Setting unidentified volume tags:")
        ebs_snapshotter.set_volume_snapshot_tag(unidentified_vol_ids, self.args.unidentified_volumes,
                                                prefix="    ", dry_run=self.args.dry_run)

        # NOTE: not setting purpose tag because volumes are unidentified, so we don't know.
        # NOTE: not setting Name tag because we don't know if it makes sense in this context.

    def main(self):
        """ Serves as the entry point for the CLI """

        logger.info('Starting snapshot tagging')

        if self.args.aws_creds_profile:
            os.environ['AWS_PROFILE'] = self.args.aws_creds_profile

        ebs_snapshotter = EbsSnapshotter(self.args.region, verbose=True)
        if not ebs_snapshotter.is_region_valid(self.args.region):
            logger.info("Invalid region")
            sys.exit(1)
        else:
            logger.info("Region: %s:", self.args.region)
            ebs_util = EbsUtil(self.args.region, verbose=True)
            ebs_snapshotter = EbsSnapshotter(self.args.region, verbose=True)

            # filter out the already tagged volumes
            skip_volume_ids = []

            if not self.args.retag_volumes:
                # They don't want us to retag volumes that are already tagged, so
                # add the already tagged volumes to the list of volume IDs to skip.
                skip_volume_ids += ebs_snapshotter.get_already_tagged_volume_ids()
                logger.info('Skipping this many volume ids: %s', len(skip_volume_ids))

            vol_ids = ebs_util.get_classified_volume_ids(skip_volume_ids)
            for id_name, id_list in vol_ids._asdict().iteritems():
                logger.info('name: %s amount: %s', id_name, len(id_list))

            ## Actually create the snapshot tags now
            if self.args.master_root_volumes and vol_ids.master_root:
                self.set_master_root_volume_tags(vol_ids.master_root, ebs_snapshotter, ebs_util)

            if self.args.node_root_volumes and vol_ids.node_root:
                self.set_node_root_volume_tags(vol_ids.node_root, ebs_snapshotter, ebs_util)

            if self.args.docker_storage_volumes and vol_ids.docker_storage:
                self.set_docker_storage_volume_tags(vol_ids.docker_storage, ebs_snapshotter, ebs_util)

            if self.args.manually_provisioned_pv_volumes and vol_ids.manually_provisioned_pv:
                self.set_manually_provisioned_pv_volume_tags(vol_ids.manually_provisioned_pv,
                                                             ebs_snapshotter, ebs_util)

            if self.args.autoprovisioned_pv_volumes and vol_ids.autoprovisioned_pv:
                self.set_autoprovisioned_pv_volume_tags(vol_ids.autoprovisioned_pv, ebs_snapshotter,
                                                        ebs_util)

            if self.args.unidentified_volumes and vol_ids.unidentified:
                self.set_unidentified_volume_tags(vol_ids.unidentified, ebs_snapshotter)

if __name__ == "__main__":
    TaggerCli().main()
