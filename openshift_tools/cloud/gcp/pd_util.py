#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a library that can identify OpenShift EBS volume types and return them.

 Usage:

    # Create Snapshots

    regions = gcp_snapshotter.PDSnapshotter.get_supported_regions(project, creds_path)

    for region in regions:
        # This example doesn't skip any volume ids, but it is highly useful to do so.
        skip_volume_names = []
        vol_ids = eu.get_classified_volume_ids(skip_volume_names)

        print vol_ids
"""


import re
import os
from collections import namedtuple
from openshift_tools.cloud.gcp.base import Base
from openshift_tools.cloud.gcp.instance_util import InstanceUtil

OpenShiftVolumeTypes = namedtuple('OpenShiftVolumeTypes',
                                  ['master_root',
                                   'node_root',
                                   'docker_storage',
                                   'autoprovisioned_pv',
                                   'manually_provisioned_pv',
                                   'unidentified'
                                  ])


PURPOSE_TAG_KEY = 'purpose'
NAME_TAG_KEY = 'Name'

# pylint: disable=too-many-public-methods
class PDUtil(Base):
    """ Useful utility methods for PDs """

    def __init__(self, project, region, creds, verbose=False):
        """ Initialize the class """
        super(PDUtil, self).__init__(project, region, creds, verbose)

        self.instance_util = InstanceUtil(project, region, creds, verbose)

    def get_instance_volume_names(self, skip_volume_names=None):
        """ Returns the volume IDs attached to different instance types. """
        master_root_volume_names = set()
        node_root_volume_names = set()
        docker_storage_volume_names = set()

        if not skip_volume_names:
            skip_volume_names = []

        # Ensure that we use a set so that we can't have multiple entries of the
        # same volume ID to skip.
        skip_volume_names = set(skip_volume_names)

        for inst in self.instances:

            hosttype = [obj['value'] for obj  in inst['metadata']['items'] if obj['key'] == 'host-type']
            if not hosttype:
                print 'Skipping instance: %s.  hosttype not detected.' % inst['name']
                continue

            hosttype = hosttype[0]

            for vol in inst['disks']:
                device = vol['deviceName']
                vol_name = os.path.basename(vol['source'])

                # We'll skip any volumes in this list. Useful to skip already labeled volumes.
                if vol_name in skip_volume_names:
                    continue

                # Etcd is stored on the root volume on the masters. This is
                # also how we backup the ca.crt private keys and other master
                # specific data.
                if hosttype == 'master' and device == 'boot' and vol['boot']:
                    # We're only going to keep the volume_id because we'll be filtering these out.
                    master_root_volume_names.add(vol_name)

                # nodes are cattle. We don't care about their root volumes.
                if hosttype == 'node' and device == 'boot' and vol['boot']:
                    node_root_volume_names.add(vol_name)

                # masters and nodes have their docker storage volume on xvdb
                if hosttype in ['master', 'node'] and device == 'docker':
                    docker_storage_volume_names.add(vol_name)

        return (master_root_volume_names, node_root_volume_names, docker_storage_volume_names)

    def get_auto_prov_pv_volume_names(self, skip_volume_names=None):
        """ Returns a list of volumes for PVs that the autoprovisioner created """
        if not skip_volume_names:
            skip_volume_names = []

        # Ensure that we use a set so that we can't have multiple entries of the
        # same volume ID to skip.
        skip_volume_names = set(skip_volume_names)

        # Identify the volumes that were autoprovisioned for PVs
        autoprovisioned_pv_volume_names = set()
        for vol in self.volumes:
            if vol['name'] in skip_volume_names:
                continue

            if "kubernetes.io/created-for" in vol['description']:
                autoprovisioned_pv_volume_names.add(vol['name'])

        return autoprovisioned_pv_volume_names

    def get_manual_prov_pv_volume_names(self, skip_volume_names=None):
        """ Returns a list of volume IDs for PVs that were created manually """
        if not skip_volume_names:
            skip_volume_names = []

        # Ensure that we use a set so that we can't have multiple entries of the
        # same volume ID to skip.
        skip_volume_names = set(skip_volume_names)

        # Identify the volumes that were manually provisioned for PVs
        retval = set()
        for vol in self.volumes:
            if vol['name'] in skip_volume_names:
                continue

            vol_name = vol['name']

            if vol_name and re.match("^pv-", vol_name):
                retval.add(vol['name'])

        return retval

    def get_classified_volume_types(self, skip_volume_names=None):
        """ Returns a DTO of all of the volume ID types identified """

        # make a set
        if not skip_volume_names:
            skip_volume_names = []

        # Ensure that we use a set so that we can't have multiple entries of the
        # same volume ID to skip.
        skip_volume_names = set(skip_volume_names)

        mnames, nnames, dsnames = self.get_instance_volume_names(skip_volume_names)

        skip_volume_names = skip_volume_names.union(mnames).union(nnames).union(dsnames)

        apnames = self.get_auto_prov_pv_volume_names(skip_volume_names)

        skip_volume_names = skip_volume_names.union(apnames)

        mpnames = self.get_manual_prov_pv_volume_names(skip_volume_names)

        skip_volume_names = skip_volume_names.union(mpnames)

        # These are all of the rest of the volumes. aka "unidentified"
        unames = [v['name'] for v in self.instances  if v['name'] not in skip_volume_names]

        return OpenShiftVolumeTypes(master_root=mnames,
                                    node_root=nnames,
                                    docker_storage=dsnames,
                                    autoprovisioned_pv=apnames,
                                    manually_provisioned_pv=mpnames,
                                    unidentified=unames
                                   )

    def set_volume_purpose_label(self, volume_names, purpose, prefix="", dry_run=False):
        """ Adds a label to the PD volume describing the purpose of this volume """
        self.verbose_print("Setting label '%s: %s' on %d volume(s): %s" % \
                           (PURPOSE_TAG_KEY, purpose, len(volume_names), volume_names),
                           prefix=prefix)

        if dry_run:
            self.print_dry_run_msg(prefix=prefix + "  ")
        else:
            for volume in volume_names:
                self.set_volume_label(volume, {PURPOSE_TAG_KEY: purpose})

            # This will trigger a fetch.  This needs to occur because once labeled the disks
            # receive an updated labelFingerprint which will prevent future relabels.
            #self.volumes = self.get_all_volumes()

