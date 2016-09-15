# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is the base class for our gcp utility classes.
"""

import os
# pylint: disable=import-error
from apiclient.discovery import build
from oauth2client.client import GoogleCredentials

# Specifically exclude certain regions
DRY_RUN_MSG = "*** DRY RUN, NO ACTION TAKEN ***"

class Base(object):
    """ Class that provides base methods for other gcp utility classes """

    # Shared by all of the utilities
    _volumes = None
    _instances = None
    _snapshots = None

    def __init__(self, project, region_name, creds_path=None, verbose=False):
        """ Initialize the class """
        if not creds_path:
            credentials = GoogleCredentials.get_application_default()
        else:
            credentials = GoogleCredentials.from_stream(creds_path)
        self._credentials = credentials
        self.scope = build('compute', 'beta', credentials=self._credentials)
        self.project = project
        self.region_name = region_name
        self._region = None
        self.verbose = verbose

    @property
    def volumes(self):
        '''property for all volumes in a region'''
        if Base._volumes == None:
            Base._volumes = self.get_all_volumes()

        return Base._volumes

    # pylint: disable=no-self-use
    @volumes.setter
    def volumes(self, vols):
        '''setter for volumes'''
        Base._volumes = vols

    @property
    def snapshots(self):
        '''property for all snapshots'''
        if Base._snapshots == None:
            Base._snapshots = self.get_all_snapshots()

        return Base._snapshots

    @snapshots.setter
    def snapshots(self, snaps):
        '''setter for snapshots'''
        Base._snapshots = snaps

    @property
    def instances(self):
        '''property for all instances in a region'''
        if Base._instances == None:
            Base._instances = self.get_all_instances()

        return Base._instances

    @instances.setter
    def instances(self, instances):
        '''setter for instances in a region'''
        Base._instances = instances

    @property
    def region(self):
        '''property for region'''
        if self._region == None:
            self._region = self.scope.regions().get(project=self.project, region=self.region_name).execute()

        return self._region

    def verbose_print(self, msg="", prefix="", end="\n"):
        """ Prints msg using prefix and end IF verbose is set on the class. """
        if self.verbose:
            print("%s%s%s") % (prefix, msg, end),

    def print_dry_run_msg(self, prefix="", end="\n"):
        """ Prints a dry run message. """
        self.verbose_print(DRY_RUN_MSG, prefix=prefix, end=end)

    def get_all_snapshots(self):
        '''return all volumes'''
        return self.scope.snapshots().list(project=self.project).execute()['items']

    def get_all_instances(self):
        '''return all instances'''
        instances = []
        for zone in self.region['zones']:
            results = self.scope.instances().list(project=self.project,
                                                  zone=os.path.basename(zone),
                                                 ).execute()
            if results.has_key('items'):
                instances.extend(results['items'])

        return instances

    def get_all_volumes(self):
        '''return all volumes'''
        vols = []
        for zone in self.region['zones']:
            results = self.scope.disks().list(project=self.project,
                                              zone=os.path.basename(zone),
                                             ).execute()
            if results.has_key('items'):
                vols.extend(results['items'])

        return vols

    @staticmethod
    def get_supported_regions(project, creds_path=None):
        """ Returns the zones that we support for the region passed."""
        credentials = None
        if creds_path == None:
            credentials = GoogleCredentials.get_application_default()
        else:
            credentials = GoogleCredentials.from_stream(creds_path)
        scope = build('compute', 'beta', credentials=credentials)
        regions = scope.regions().list(project=project).execute()['items']

        supported_regions = [reg for reg in regions if not reg.has_key('deprecated')]

        return supported_regions

    def print_volume(self, volume, prefix=""):
        """ Prints out the details of the given volume. """
        self.verbose_print("%s:" % volume['name'], prefix=prefix)
        self.verbose_print("  Tags:", prefix=prefix)

        for key, val in volume['labels'].items():
            self.verbose_print("    %s: %s" % (key, val), prefix=prefix)

    def print_snapshots(self, snapshots, msg=None, prefix=""):
        """ Prints out the details for the given snapshots. """
        if msg:
            self.verbose_print(msg, prefix=prefix)

        for snap in snapshots:
            self.verbose_print("  %s: start_time %s" % (snap['name'], snap['creationTimestamp']), prefix=prefix)

    def get_volume_by_name(self, vol_name):
        '''return a volume by its name'''
        for vol in self.volumes:
            if vol['name'] == vol_name:
                return vol

        return None

    def get_snapshot_by_name(self, snap_name):
        '''return a snap by its name'''
        for snap in self.get_all_snapshots():
            if snap['name'] == snap_name:
                return snap

        return None

    def update_snapshots(self, upd_snap):
        '''replace volume in self.snapshots'''
        for idx, snap in enumerate(self.snapshots):
            if snap['name'] == upd_snap['name']:
                self.snapshots[idx] = upd_snap
                break
        else:
            self.snapshots.append(upd_snap)

        return True

    def update_volume(self, upd_vol):
        '''replace volume in self.volumes'''
        for idx, vol in enumerate(self.volumes):
            if vol['name'] == upd_vol['name']:
                self.volumes[idx] = upd_vol
                break
        else:
            self.volumes.append(upd_vol)

        return True

    def refresh_snapshot(self, snap_name):
        '''return a snapshot'''
        return  self.scope.snapshots().get(project=self.project, snapshot=snap_name,).execute()

    def refresh_volume(self, vol_name, zone):
        '''return a volume'''
        return  self.scope.disks().get(project=self.project, zone=zone, disk=vol_name).execute()

    def set_volume_label(self, volume_name, labels):
        '''call setLabels on a volume'''
        volume = self.get_volume_by_name(volume_name)

        body = {}
        body['labels'] = {}

        if volume.has_key('labels'):
            body['labels'] = volume['labels'].copy()

        if not labels:
            # we wanted empty labels
            body['labels'] = {}

        elif isinstance(labels, dict):
            body['labels'].update(labels)

        body['labelFingerprint'] = volume['labelFingerprint']

        result = self.scope.disks().setLabels(project=self.project,
                                              zone=os.path.basename(volume['zone']),
                                              resource=volume['name'],
                                              body=body,
                                             ).execute()
        # Upon updating the labels the labelFingerprint changes.  This needs to be refreshed.
        fresh_vol = self.refresh_volume(volume['name'], os.path.basename(volume['zone']))
        self.update_volume(fresh_vol)

        return result

    def set_snapshot_label(self, snap_name, labels):
        '''call setLabels on a snapshot'''
        snapshot = self.get_snapshot_by_name(snap_name)

        body = {}
        body['labels'] = {}

        if snapshot.has_key('labels'):
            body['labels'] = snapshot['labels'].copy()

        if not labels:
            # we wanted empty labels
            body['labels'] = {}

        elif isinstance(labels, dict):
            body['labels'].update(labels)

        body['labelFingerprint'] = snapshot['labelFingerprint']

        result = self.scope.snapshots().setLabels(project=self.project,
                                                  resource=snapshot['name'],
                                                  body=body,
                                                 ).execute()

        # Upon updating the labels the labelFingerprint changes.  This needs to be refreshed.
        fresh_snap = self.refresh_snapshot(snapshot['name'])
        self.update_snapshots(fresh_snap)

        print 'snapshot result'
        print result
        return result
