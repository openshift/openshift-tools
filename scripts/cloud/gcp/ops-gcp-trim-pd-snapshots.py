#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a script that snapshots all volumes in a given account.

 The volumes must be tagged like so:
 snapshot: daily
 snapshot: weekly

 Usage:

 ops-gcp-trim-pd-snapshots.py --keep-hourly 10 --gcp-creds-file /root/.gce/creds.json

"""
# Ignoring module name
# pylint: disable=invalid-name,import-error

import json
import argparse
from openshift_tools.cloud.gcp import gcp_snapshotter

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender

EXPIRED_SNAPSHOTS_KEY = 'gcp.pd.snapshotter.expired_snapshots'
DELETED_SNAPSHOTS_KEY = 'gcp.pd.snapshotter.deleted_snapshots'
DELETION_ERRORS_KEY = 'gcp.pd.snapshotter.deletion_errors'

class TrimmerCli(object):
    """ Responsible for parsing cli args and running the trimmer. """
    def __init__(self):
        """ initialize the class """
        self.args = None
        self.parse_args()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='PD Snapshot Trimmer')
        parser.add_argument('--keep-hourly', required=True, type=int,
                            help='The number of hourly snapshots to keep. 0 is infinite.')
        parser.add_argument('--keep-daily', required=True, type=int,
                            help='The number of daily snapshots to keep. 0 is infinite.')
        parser.add_argument('--keep-weekly', required=True, type=int,
                            help='The number of weekly snapshots to keep. 0 is infinite.')
        parser.add_argument('--keep-monthly', required=True, type=int,
                            help='The number of monthly snapshots to keep. 0 is infinite.')
        parser.add_argument('--gcp-creds-file', required=False,
                            help='The gcp credentials file to use.')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Say what would have been done, but don\'t actually do it.')

        self.args = parser.parse_args()


    def main(self):
        """ main function """

        total_expired_snapshots = 0
        total_deleted_snapshots = 0
        total_deletion_errors = 0

        creds = json.loads(open(self.args.gcp_creds_file).read())

        regions = gcp_snapshotter.PDSnapshotter.get_supported_regions(creds['project_id'], self.args.gcp_creds_file)

        for region in regions:
            print "Region: %s:" % region
            ss = gcp_snapshotter.PDSnapshotter(creds['project_id'],
                                               region['name'],
                                               self.args.gcp_creds_file,
                                               verbose=True)

            expired_snapshots, deleted_snapshots, snapshot_deletion_errors = \
                ss.trim_snapshots(hourly_backups=self.args.keep_hourly, \
                                  daily_backups=self.args.keep_daily, \
                                  weekly_backups=self.args.keep_weekly, \
                                  monthly_backups=self.args.keep_monthly, \
                                  dry_run=self.args.dry_run)

            num_deletion_errors = len(snapshot_deletion_errors)

            total_expired_snapshots += len(expired_snapshots)
            total_deleted_snapshots += len(deleted_snapshots)
            total_deletion_errors += num_deletion_errors

            if num_deletion_errors > 0:
                print "  Snapshot Deletion errors (%d):" % num_deletion_errors
                for cur_err in snapshot_deletion_errors:
                    print "    %s" % cur_err

        print
        print "       Total number of expired snapshots: %d" % total_expired_snapshots
        print "       Total number of deleted snapshots: %d" % total_deleted_snapshots
        print "Total number of snapshot deletion errors: %d" % total_deletion_errors
        print


        print "Sending results to Zabbix:"
        if self.args.dry_run:
            print "  *** DRY RUN, NO ACTION TAKEN ***"
        else:
            TrimmerCli.report_to_zabbix(total_expired_snapshots, total_deleted_snapshots, total_deletion_errors)


    @staticmethod
    def report_to_zabbix(total_expired_snapshots, total_deleted_snapshots, total_deletion_errors):
        """ Sends the commands exit code to zabbix. """
        mts = MetricSender(verbose=True)

        mts.add_metric({
            EXPIRED_SNAPSHOTS_KEY: total_expired_snapshots,
            DELETED_SNAPSHOTS_KEY: total_deleted_snapshots,
            DELETION_ERRORS_KEY: total_deletion_errors
        })

        mts.send_metrics()

if __name__ == "__main__":
    TrimmerCli().main()
