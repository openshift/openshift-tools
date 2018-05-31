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
# pylint: disable=invalid-name,import-error

import os
import sys
import argparse
import logging
from logging.handlers import RotatingFileHandler

from openshift_tools.cloud.aws import ebs_snapshotter

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logFile = '/var/log/ec2-trim-ebs-snapshots.log'

logRFH = RotatingFileHandler(logFile, mode='a', maxBytes=2*1024*1024, backupCount=5, delay=0)
logRFH.setFormatter(logFormatter)
logRFH.setLevel(logging.INFO)
logger.addHandler(logRFH)
logConsole = logging.StreamHandler()
logConsole.setFormatter(logFormatter)
logConsole.setLevel(logging.WARNING)
logger.addHandler(logConsole)


EXPIRED_SNAPSHOTS_KEY = 'aws.ebs.snapshotter.expired_snapshots'
DELETED_SNAPSHOTS_KEY = 'aws.ebs.snapshotter.deleted_snapshots'
DELETION_ERRORS_KEY = 'aws.ebs.snapshotter.deletion_errors'

class TrimmerCli(object):
    """ Responsible for parsing cli args and running the trimmer. """
    def __init__(self):
        """ initialize the class """
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
        parser.add_argument('--sleep-between-delete', required=False, type=float, default=0.0,
                            help='The amount of time to sleep between snapshot delete API calls.')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='Say what would have been done, but don\'t actually do it.')
        parser.add_argument('--delete-orphans-older-than', required=True, type=int,
                            help='Delete orphaned snapshots if they are older than given days')
        parser.add_argument('--region', required=True,
                            help='The region that we want to process snapshots in')
        parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
        parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
        parser.add_argument('--skip-boto-logs', action='store_true', default=False, help='Skip boto logs')

        self.args = parser.parse_args()

    def main(self):
        """ main function """

        logger.info('Starting snapshot trimming')

        total_expired_snapshots = 0
        total_deleted_snapshots = 0
        total_orphans_deleted = 0
        total_deletion_errors = 0

        if self.args.aws_creds_profile:
            os.environ['AWS_PROFILE'] = self.args.aws_creds_profile

        if not ebs_snapshotter.EbsSnapshotter.is_region_valid(self.args.region):
            logger.info("Invalid region")
            sys.exit(1)
        else:
            logger.info("Region: %s:", self.args.region)
            ss = ebs_snapshotter.EbsSnapshotter(self.args.region, verbose=True)

            (expired_snapshots,
             deleted_snapshots,
             deleted_orphans,
             snapshot_deletion_errors) = ss.trim_snapshots(
                 hourly_backups=self.args.keep_hourly,
                 daily_backups=self.args.keep_daily,
                 weekly_backups=self.args.keep_weekly,
                 monthly_backups=self.args.keep_monthly,
                 dry_run=self.args.dry_run,
                 delete_orphans_older_than=self.args.delete_orphans_older_than,
                 sleep_between_delete=self.args.sleep_between_delete)

            num_deletion_errors = len(snapshot_deletion_errors)

            total_expired_snapshots += len(expired_snapshots)
            total_deleted_snapshots += len(deleted_snapshots)
            total_orphans_deleted += deleted_orphans
            total_deletion_errors += num_deletion_errors

            if num_deletion_errors > 0:
                logger.info("  Snapshot Deletion errors (%d):", num_deletion_errors)
                for cur_err in snapshot_deletion_errors:
                    logger.info("%s", cur_err)

        logger.info("Total number of expired snapshots: %d", total_expired_snapshots)
        logger.info("Total number of deleted snapshots: %d", total_deleted_snapshots)
        logger.info("Total number of orphaned snapshots deleted: %d", total_orphans_deleted)
        logger.info("Total number of snapshot deletion errors: %d", total_deletion_errors)

        if self.args.dry_run:
            logger.info("*** DRY RUN, NO ACTION TAKEN ***")
        else:
            logger.debug('Sending values to zabbix')
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
