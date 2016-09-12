#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a script that snapshots all volumes in a given account.

 The volumes must be tagged like so:
 snapshot: daily
 snapshot: weekly

 This assumes that your AWS credentials are loaded in the ENV variables:
  AWS_ACCESS_KEY_ID=xxxx
  AWS_SECRET_ACCESS_KEY=xxxx

 Usage:

 ops-ec2-snapshot-ebs-volumes.py --with-schedule weekly

"""
# Ignoring module name
# pylint: disable=invalid-name

import json
import argparse
# pylint: disable=import-error
from openshift_tools.cloud.gcp import gcp_snapshotter

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender


EBS_SNAPSHOTTER_DISC_KEY = 'disc.gcp.pd.snapshotter'
EBS_SNAPSHOTTER_DISC_SCHEDULE_MACRO = '#OSO_SNAP_SCHEDULE'
EBS_SNAPSHOTTER_SNAPSHOTTABLE_VOLUMES_KEY = 'disc.gcp.pd.snapshotter.snapshottable_volumes'
EBS_SNAPSHOTTER_SNAPSHOTS_CREATED_KEY = 'disc.gcp.pd.snapshotter.snapshots_created'
EBS_SNAPSHOTTER_SNAPSHOT_CREATION_ERRORS_KEY = 'disc.gcp.pd.snapshotter.snapshot_creation_errors'

class SnapshotterCli(object):
    """ Responsible for parsing cli args and running the snapshotter. """

    def __init__(self):
        """ initialize the class """
        self.args = None
        self.parse_args()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='EBS Snapshotter')
        parser.add_argument('--with-schedule', choices=gcp_snapshotter.SUPPORTED_SCHEDULES,
                            required=True,
                            help='The schedule for the PD volumes to be snapshotted ' + \
                                 '(i.e. the value of the \'snapshot\' tag on the volumes).')
        parser.add_argument('--gcp-creds-file', required=False,
                            help='The GCP credentials to use.')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Say what would have been done, but don\'t actually do it.')

        self.args = parser.parse_args()

    def main(self):
        """ main function """

        total_snapshottable_vols = 0
        total_snapshots_created = 0
        total_snapshot_creation_errors = 0

        creds = json.loads(open(self.args.gcp_creds_file).read())

        regions = gcp_snapshotter.PDSnapshotter.get_supported_regions(creds['project_id'], self.args.gcp_creds_file)

        for region in regions:
            print "Region: %s:" % region
            ss = gcp_snapshotter.PDSnapshotter(creds['project_id'],
                                               region['name'],
                                               self.args.gcp_creds_file,
                                               verbose=True)

            avail_vols, snapshots_created, snapshot_creation_errors = \
                ss.create_snapshots(self.args.with_schedule, dry_run=self.args.dry_run)

            num_creation_errors = len(snapshot_creation_errors)

            total_snapshottable_vols += len(avail_vols)
            total_snapshots_created += len(snapshots_created)
            total_snapshot_creation_errors += num_creation_errors

            if num_creation_errors > 0:
                print "  Snapshot Deletion errors (%d):" % num_creation_errors
                for cur_err in snapshot_creation_errors:
                    print "    %s" % cur_err


        print
        print "    Total number of snapshottable volumes: %d" % total_snapshottable_vols
        print "        Total number of snapshots created: %d" % total_snapshots_created
        print "Total number of snapshots creation errors: %d" % total_snapshot_creation_errors
        print

        print "Sending results to Zabbix:"
        if self.args.dry_run:
            print "  *** DRY RUN, NO ACTION TAKEN ***"
        else:
            #TODO: uncomment
            pass
            #self.report_to_zabbix(total_snapshottable_vols, total_snapshots_created, total_snapshot_creation_errors)

    def report_to_zabbix(self, total_snapshottable_vols, total_snapshots_created, total_snapshot_creation_errors):
        """ Sends the commands exit code to zabbix. """
        zs = ZaggSender(verbose=True)


        # Populate EBS_SNAPSHOTTER_DISC_SCHEDULE_MACRO with the schedule
        zs.add_zabbix_dynamic_item(EBS_SNAPSHOTTER_DISC_KEY, EBS_SNAPSHOTTER_DISC_SCHEDULE_MACRO, \
                                   [self.args.with_schedule])

        # Send total_snapshottable_vols prototype item key and value
        zs.add_zabbix_keys({'%s[%s]' % (EBS_SNAPSHOTTER_SNAPSHOTTABLE_VOLUMES_KEY, self.args.with_schedule): \
                           total_snapshottable_vols})

        # Send total_snapshots_created prototype item key and value
        zs.add_zabbix_keys({'%s[%s]' % (EBS_SNAPSHOTTER_SNAPSHOTS_CREATED_KEY, self.args.with_schedule): \
                           total_snapshots_created})

        # Send total_snapshot_creation_errors prototype item key and value
        zs.add_zabbix_keys({'%s[%s]' % (EBS_SNAPSHOTTER_SNAPSHOT_CREATION_ERRORS_KEY, self.args.with_schedule): \
                           total_snapshot_creation_errors})


        # Actually send them
        zs.send_metrics()


if __name__ == "__main__":
    SnapshotterCli().main()
