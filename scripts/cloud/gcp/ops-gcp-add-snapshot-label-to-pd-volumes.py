#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a script that can be used to label PD volumes in OpenShift v3.

 This script assume that your GCP credentials are setup in ~/.gce/creds.json like this:

"""
# Ignoring module name
# pylint: disable=invalid-name

import argparse
import json

# pylint: disable=import-error
from openshift_tools.cloud.gcp.gcp_snapshotter import SUPPORTED_SCHEDULES, PDSnapshotter
from openshift_tools.cloud.gcp.pd_util import PDUtil

TAGGER_SUPPORTED_SCHEDULES = ['never'] + SUPPORTED_SCHEDULES


ROOT_VOLUME_PURPOSE = "root-volume"
DOCKER_VOLUME_PURPOSE = "docker-storage-volume"
PV_PURPOSE = "customer-persistent-volume"


class TaggerCli(object):
    """ Implements the cli interface to the GCP snapshot labeler. """
    def __init__(self):
        self.args = None
        self.parse_args()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='EBS Volume Tagger')
        parser.add_argument('--master-root-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that master root volumes ' + \
                                 'should be labeled with.')
        parser.add_argument('--node-root-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that node root volumes ' + \
                                 'should be labeled with.')
        parser.add_argument('--docker-storage-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that docker storage ' + \
                                 'volumes should be labeled with.')
        parser.add_argument('--autoprovisioned-pv-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that autoprovisioned pv ' + \
                                 'volumes should be labeled with.')
        parser.add_argument('--manually-provisioned-pv-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that manually provisioned pv ' + \
                                 'volumes should be labeled with.')
        parser.add_argument('--unidentified-volumes', choices=TAGGER_SUPPORTED_SCHEDULES,
                            help='The snapshot schedule that unidentified ' + \
                                 'volumes should be labeled with.')
        parser.add_argument('--set-name-label', action='store_true', default=False,
                            help='Add the Name label to volumes of the host where this ' + \
                                 'volume is attached.')
        parser.add_argument('--set-purpose-label', action='store_true', default=False,
                            help='Add the purpose label to volumes')
        parser.add_argument('--relabel-volumes', action='store_true', default=False,
                            help='Relabel volumes that already have a snapshot label. ' + \
                                 'DANGEROUS - Only do this if you know what you\'re doing!')
        parser.add_argument('--gcp-creds-file', required=False,
                            help='The GCP credentials file to use.')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Say what would have been done, but don\'t actually do it.')

        self.args = parser.parse_args()

    def set_master_root_volume_labels(self, master_root_vols, gcp_snapshotter, pd_util):
        """ Sets labels on master root volumes """
        print
        print "  Setting master root volume labels:"
        gcp_snapshotter.set_volume_snapshot_label(master_root_vols, self.args.master_root_volumes,
                                                  prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_purpose_label:
            pd_util.set_volume_purpose_label(master_root_vols, ROOT_VOLUME_PURPOSE,
                                             prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_name_label:
            pd_util.set_volume_name_label(master_root_vols, prefix="    ", dry_run=self.args.dry_run)

    def set_node_root_volume_labels(self, node_root_vols, gcp_snapshotter, pd_util):
        """ Sets labels on node root volumes """
        print
        print "  Setting node root volume labels:"
        gcp_snapshotter.set_volume_snapshot_label(node_root_vols, self.args.node_root_volumes,
                                                  prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_purpose_label:
            pd_util.set_volume_purpose_label(node_root_vols, ROOT_VOLUME_PURPOSE,
                                             prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_name_label:
            pd_util.set_volume_name_label(node_root_vols, prefix="    ", dry_run=self.args.dry_run)

    def set_docker_storage_volume_labels(self, docker_storage_vols, gcp_snapshotter, pd_util):
        """ Sets labels on docker storage volumes """
        print
        print "  Setting docker storage volume labels:"
        gcp_snapshotter.set_volume_snapshot_label(docker_storage_vols, self.args.docker_storage_volumes,
                                                  prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_purpose_label:
            pd_util.set_volume_purpose_label(docker_storage_vols, DOCKER_VOLUME_PURPOSE,
                                             prefix="    ", dry_run=self.args.dry_run)

        if self.args.set_name_label:
            pd_util.set_volume_name_label(docker_storage_vols, prefix="    ", dry_run=self.args.dry_run)

    def set_manually_provisioned_pv_volume_labels(self, manually_provisioned_pv_vols, gcp_snapshotter, pd_util):
        """ Sets labels on manually provisioned pv volumes """
        print
        print "  Setting manually provisioned pv volume labels:"
        gcp_snapshotter.set_volume_snapshot_label(manually_provisioned_pv_vols,
                                                  self.args.manually_provisioned_pv_volumes,
                                                  prefix="    ", dry_run=self.args.dry_run)

        # NOTE: not setting Name label because PVs don't belong to a specific host.

        if self.args.set_purpose_label:
            pd_util.set_volume_purpose_label(manually_provisioned_pv_vols, PV_PURPOSE,
                                             prefix="    ", dry_run=self.args.dry_run)

    def set_autoprovisioned_pv_volume_labels(self, autoprovisioned_pv_vols, gcp_snapshotter, pd_util):
        """ Sets labels on autoprovisioned pv volumes """
        print
        print "  Setting autoprovisioned pv volume labels:"
        gcp_snapshotter.set_volume_snapshot_label(autoprovisioned_pv_vols,
                                                  self.args.autoprovisioned_pv_volumes,
                                                  prefix="    ", dry_run=self.args.dry_run)

        # NOTE: not setting Name label because PVs don't belong to a specific host.

        if self.args.set_purpose_label:
            pd_util.set_volume_purpose_label(autoprovisioned_pv_vols, PV_PURPOSE,
                                             prefix="    ", dry_run=self.args.dry_run)

    def set_unidentified_volume_labels(self, unidentified_vols, gcp_snapshotter):
        """ Sets labels on unidentified pv volumes """
        print
        print "  Setting unidentified volume labels:"
        gcp_snapshotter.set_volume_snapshot_label(unidentified_vols, self.args.unidentified_volumes,
                                                  prefix="    ", dry_run=self.args.dry_run)

        # NOTE: not setting purpose label because volumes are unidentified, so we don't know.
        # NOTE: not setting Name label because we don't know if it makes sense in this context.

    def main(self):
        """ Serves as the entry point for the CLI """
        creds = json.loads(open(self.args.gcp_creds_file).read())
        project = creds['project_id']

        for region in PDUtil.get_supported_regions(project, self.args.gcp_creds_file):
            print
            print "Region: %s:" % region
            pd_util = PDUtil(project, region['name'], self.args.gcp_creds_file, verbose=True)
            gcp_snapshotter = PDSnapshotter(project, region['name'], self.args.gcp_creds_file, verbose=True)

            # filter out the already labeled volumes
            skip_volumes = []

            if not self.args.relabel_volumes:
                # They don't want us to relabel volumes that are already labeled, so
                # add the already labeled volumes to the list of volume IDs to skip.
                skip_volumes += [vol['name'] for vol in gcp_snapshotter.get_already_labeled_volumes()]

            vols = pd_util.get_classified_volume_types(skip_volumes)

            ## Actually create the snapshot labels now
            if self.args.master_root_volumes and vols.master_root:
                self.set_master_root_volume_labels(vols.master_root, gcp_snapshotter, pd_util)

            if self.args.node_root_volumes and vols.node_root:
                self.set_node_root_volume_labels(vols.node_root, gcp_snapshotter, pd_util)

            if self.args.docker_storage_volumes and vols.docker_storage:
                self.set_docker_storage_volume_labels(vols.docker_storage, gcp_snapshotter, pd_util)

            if self.args.manually_provisioned_pv_volumes and vols.manually_provisioned_pv:
                self.set_manually_provisioned_pv_volume_labels(vols.manually_provisioned_pv,
                                                               gcp_snapshotter, pd_util)

            if self.args.autoprovisioned_pv_volumes and vols.autoprovisioned_pv:
                self.set_autoprovisioned_pv_volume_labels(vols.autoprovisioned_pv, gcp_snapshotter,
                                                          pd_util)

            if self.args.unidentified_volumes and vols.unidentified:
                self.set_unidentified_volume_labels(vols.unidentified, gcp_snapshotter)

if __name__ == "__main__":
    TaggerCli().main()
