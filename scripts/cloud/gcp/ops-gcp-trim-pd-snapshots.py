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

import os
import argparse
from openshift_tools.cloud.aws import ebs_snapshotter

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender

EXPIRED_SNAPSHOTS_KEY = 'aws.ebs.snapshotter.expired_snapshots'
DELETED_SNAPSHOTS_KEY = 'aws.ebs.snapshotter.deleted_snapshots'
DELETION_ERRORS_KEY = 'aws.ebs.snapshotter.deletion_errors'

class TrimmerCli(object):
    """ Responsible for parsing cli args and running the trimmer. """
    def __init__(self):
        """ initialize the class """
        self.args = None
        self.parse_args()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='EBS Snapshot Trimmer')
        parser.add_argument('--keep-hourly', required=True, type=int,
                            help='The number of hourly snapshots to keep. 0 is infinite.')
        parser.add_argument('--keep-daily', required=True, type=int,
                            help='The number of daily snapshots to keep. 0 is infinite.')
        parser.add_argument('--keep-weekly', required=True, type=int,
                            help='The number of weekly snapshots to keep. 0 is infinite.')
        parser.add_argument('--keep-monthly', required=True, type=int,
                            help='The number of monthly snapshots to keep. 0 is infinite.')
        parser.add_argument('--aws-creds-profile', required=False,
                            help='The AWS credentials profile to use.')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Say what would have been done, but don\'t actually do it.')

        self.args = parser.parse_args()


    def main(self):
        """ main function """

        total_expired_snapshots = 0
        total_deleted_snapshots = 0
        total_deletion_errors = 0

        if self.args.aws_creds_profile:
            os.environ['AWS_PROFILE'] = self.args.aws_creds_profile

        regions = ebs_snapshotter.EbsSnapshotter.get_supported_regions()

        for region in regions:
            print "Region: %s:" % region
            ss = ebs_snapshotter.EbsSnapshotter(region.name, verbose=True)

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
        zs = ZaggSender(verbose=True)

        zs.add_zabbix_keys({
            EXPIRED_SNAPSHOTS_KEY: total_expired_snapshots,
            DELETED_SNAPSHOTS_KEY: total_deleted_snapshots,
            DELETION_ERRORS_KEY: total_deletion_errors
        })

        zs.send_metrics()

if __name__ == "__main__":
    TrimmerCli().main()
