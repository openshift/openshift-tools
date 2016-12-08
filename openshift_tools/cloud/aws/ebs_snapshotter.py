# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a library that can snapshot EBS volumes, and trim existing snapshots.

 The volumes must be tagged like so:
 snapshot: daily
 snapshot: weekly

 Usage:

    # Create Snapshots

    regions = ebs_snapshotter.EbsSnapshotter.get_supported_regions()

    script_name = os.path.basename(__file__)

    for region in regions:
        dry_run = False
        schedule = 'daily'

        ss = ebs_snapshotter.EbsSnapshotter(region.name, verbose=True)

        avail_vols, snapshots_created, snapshot_creation_errors = \
            ss.create_snapshots(schedule, script_name, dry_run=dry_run)



    # Trim Snapshots
    dry_run = False

    regions = ebs_snapshotter.EbsSnapshotter.get_supported_regions()

    for region in regions:
        ss = ebs_snapshotter.EbsSnapshotter(region.name, verbose=True)

        expired_snapshots, deleted_snapshots, snapshot_deletion_errors = \
            ss.trim_snapshots(hourly_backups=25, \
                              daily_backups=30, \
                              weekly_backups=10, \
                              monthly_backups=12, \
                              dry_run=dry_run)
"""

from openshift_tools.cloud.aws.base import Base
from openshift_tools.cloud.aws.instance_util import InstanceUtil

from datetime import datetime
from datetime import timedelta

from time import sleep

from boto.exception import EC2ResponseError

SNAP_TAG_KEY = 'snapshot'

SUPPORTED_SCHEDULES = ['hourly', 'daily', 'weekly', 'monthly']
ALL_SCHEDULES = 'all'

class EbsSnapshotter(Base):
    """ Class responsible for creating and removing EBS snapshots """

    def __init__(self, region, verbose=False):
        """ Initialize the class """
        super(EbsSnapshotter, self).__init__(region, verbose)

        self.instance_util = InstanceUtil(region, verbose)

    def set_volume_snapshot_tag(self, volume_ids, schedule, prefix="", dry_run=False):
        """ Sets a tag to the EBS volume for snapshotting purposes """
        self.verbose_print("Setting tag '%s: %s' on %d volume(s): %s" % \
                           (SNAP_TAG_KEY, schedule, len(volume_ids), volume_ids),
                           prefix=prefix)

        if dry_run:
            self.print_dry_run_msg(prefix=prefix + "  ")
        else:
            self.ec2.create_tags(list(volume_ids), {SNAP_TAG_KEY: schedule})

    def get_already_tagged_volume_ids(self):
        """ Returns a list of volumes that already have the snapshot tag. """
        return [v.id for v in self.ec2.get_all_volumes() if v.tags.get(SNAP_TAG_KEY) != None]

    def get_volumes_with_schedule(self, schedule):
        """ Returns the volumes that are tagged in AWS with the defined schedule.

            Example volume tag:
                snapshot: daily
        """
        if schedule != ALL_SCHEDULES and schedule not in SUPPORTED_SCHEDULES:
            raise NotImplementedError

        vols = self.ec2.get_all_volumes(filters={'tag-key': SNAP_TAG_KEY})

        # They want all of the volumes with a schedule, not just e.g. 'daily'
        if schedule == ALL_SCHEDULES:
            return vols

        vols_w_sched = [v for v in vols if v.tags[SNAP_TAG_KEY].lower() == schedule.lower()]

        return vols_w_sched

    def create_snapshots(self, schedule, script_name=None, dry_run=False, sleep_between_snaps=0):
        """ Creates a snapshot for volumes tagged with the given schedule. """

        if schedule not in SUPPORTED_SCHEDULES:
            raise NotImplementedError

        snapshots = []
        errors = []
        description = "%s snapshot taken" % schedule

        if script_name:
            description += " by %s" % script_name

        volumes = self.get_volumes_with_schedule(schedule)
        all_instances = self.instance_util.get_all_instances_as_dict()

        self.verbose_print("Creating %s snapshot for:" % schedule, prefix="  ")

        for volume in volumes:
            self.print_volume(volume, prefix="    ")

            sleep(sleep_between_snaps)

            try:
                if dry_run:
                    self.print_dry_run_msg(prefix="    ")
                else:
                    new_snapshot = volume.create_snapshot(description=description)
                    inst_id = volume.attach_data.instance_id
                    inst_name = None

                    if inst_id:
                        inst_name = all_instances[inst_id].tags.get('Name')

                    attach_data = "%s:%s:%s:%s" % (volume.attach_data.status, \
                                                inst_id, \
                                                inst_name, \
                                                volume.attach_data.device)

                    # Take all of the volume's tags (including Name) and add the attachment data.
                    snap_tags = volume.tags.copy()
                    snap_tags['attach_data'] = attach_data

                    # We want the snapshot to have as much identifying information as possible.
                    new_snapshot.add_tags(snap_tags)

                    snapshots.append(new_snapshot)
            # Reason: disable pylint broad-except because we want to continue on error.
            # Status: permanently disabled
            # pylint: disable=broad-except
            except Exception as ex:
                if isinstance(ex, EC2ResponseError) and \
                   ex.error_code == "SnapshotCreationPerVolumeRateExceeded":
                    # This message means that a snapshot of this volume was recently taken,
                    # which we're trying to do anyway. So, we can safely ignore this error.

                    # Add that latest snapshot to the list of snapshots.
                    ex_snaps = volume.snapshots()
                    self.sort_snapshots(ex_snaps)
                    snapshots.append(ex_snaps[-1])
                else:
                    errors.append(ex)

            self.verbose_print()

        self.verbose_print("Number of volumes to snapshot: %d: %s" % (len(volumes), volumes), \
                           prefix="  ")
        self.verbose_print("Number of snapshots taken: %d: %s" % (len(snapshots), snapshots), \
                           prefix="  ")
        self.verbose_print("Number of snapshot creation errors: %d" % len(errors), prefix="  ")
        self.verbose_print()

        return (volumes, snapshots, errors)

    @staticmethod
    def sort_snapshots(snaps):
        """ Sorts the list of snapshots by their start times. """
        # Comparison function that compares the start times of the snapshots
        snap_start_time_cmp = lambda a, b: cmp(datetime.strptime(a.start_time[:-5], '%Y-%m-%dT%H:%M:%S'),
                                               datetime.strptime(b.start_time[:-5], '%Y-%m-%dT%H:%M:%S'))

        snaps.sort(cmp=snap_start_time_cmp)


    #
    # This function was taken and modified from boto v2: http://bit.ly/1ZUtegR
    #
    # Reason: disable pylint too-many-locals, invalid-name and too-many-branches because
    #         this is code taken from boto v2.
    # Status: permanently disabled
    # pylint: disable=too-many-locals,invalid-name,too-many-branches
    @staticmethod
    def get_expired_snapshots(snapshots, hourly_backups, daily_backups, weekly_backups, monthly_backups):
        """
        Expired snapshots, based on when they were taken. More current
        snapshots are retained, with the number retained decreasing as you
        move back in time.
        If ebs volumes have a 'Name' tag with a value, their snapshots
        will be assigned the same tag when they are created. The values
        of the 'Name' tags for snapshots are used by this function to
        group snapshots taken from the same volume (or from a series
        of like-named volumes over time) for trimming.
        For every group of like-named snapshots, this function retains
        the newest and oldest snapshots, as well as, by default,  the
        first snapshots taken in each of the last eight hours, the first
        snapshots taken in each of the last seven days, the first snapshots
        taken in the last 4 weeks (counting Midnight Sunday morning as
        the start of the week), and the first snapshot from the first
        day of each month forever.
        :type hourly_backups: int
        :param hourly_backups: How many recent hourly backups should be saved.
        :type daily_backups: int
        :param daily_backups: How many recent daily backups should be saved.
        :type weekly_backups: int
        :param weekly_backups: How many recent weekly backups should be saved.
        :type monthly_backups: int
        :param monthly_backups: How many monthly backups should be saved. Use True for no limit.
        """

        # This function first builds up an ordered list of target times
        # that snapshots should be saved for (last 8 hours, last 7 days, etc.).
        # Then a map of snapshots is constructed, with the keys being
        # the snapshot / volume names and the values being arrays of
        # chronologically sorted snapshots.
        # Finally, for each array in the map, we go through the snapshot
        # array and the target time array in an interleaved fashion,
        # deleting snapshots whose start_times don't immediately follow a
        # target time (we delete a snapshot if there's another snapshot
        # that was made closer to the preceding target time).

        snaps_to_trim = []

        now = datetime.utcnow()
        last_hour = datetime(now.year, now.month, now.day, now.hour)
        last_midnight = datetime(now.year, now.month, now.day)
        last_sunday = datetime(now.year, now.month, now.day) - timedelta(days=(now.weekday() + 1) % 7)
        start_of_month = datetime(now.year, now.month, 1)

        target_backup_times = []

        # there are no snapshots older than 1/1/2007
        oldest_snapshot_date = datetime(2007, 1, 1)

        for hour in range(0, hourly_backups):
            target_backup_times.append(last_hour - timedelta(hours=hour))

        for day in range(0, daily_backups):
            target_backup_times.append(last_midnight - timedelta(days=day))

        for week in range(0, weekly_backups):
            target_backup_times.append(last_sunday - timedelta(weeks=week))

        one_day = timedelta(days=1)
        monthly_snapshots_added = 0
        while (start_of_month > oldest_snapshot_date and
               (monthly_backups is True or
                monthly_snapshots_added < monthly_backups)):
            # append the start of the month to the list of
            # snapshot dates to save:
            target_backup_times.append(start_of_month)
            monthly_snapshots_added += 1
            # there's no timedelta setting for one month, so instead:
            # decrement the day by one, so we go to the final day of
            # the previous month...
            start_of_month -= one_day
            # ... and then go to the first day of that previous month:
            start_of_month = datetime(start_of_month.year,
                                      start_of_month.month, 1)

        temp = []

        for t in target_backup_times:
            if temp.__contains__(t) == False:
                temp.append(t)

        # sort to make the oldest dates first, and make sure the month start
        # and last four week's start are in the proper order
        target_backup_times = sorted(temp)

        # The snapshots MUST be sorted for this to work properly
        EbsSnapshotter.sort_snapshots(snapshots)

        # Do a running comparison of snapshot dates to desired time
        # periods, keeping the oldest snapshot in each
        # time period and deleting the rest:

        tmpsnaps = snapshots[:-1] # never delete the newest snapshot
        time_period_number = 0
        snap_found_for_this_time_period = False
        for snap in tmpsnaps:
            check_this_snap = True
            while check_this_snap and time_period_number < target_backup_times.__len__():
                snap_date = datetime.strptime(snap.start_time,
                                              '%Y-%m-%dT%H:%M:%S.000Z')
                if snap_date < target_backup_times[time_period_number]:
                    # the snap date is before the cutoff date.
                    # Figure out if it's the first snap in this
                    # date range and act accordingly (since both
                    #date the date ranges and the snapshots
                    # are sorted chronologically, we know this
                    #snapshot isn't in an earlier date range):
                    if snap_found_for_this_time_period == True:
                        if not snap.tags.get('preserve_snapshot'):
                            # as long as the snapshot wasn't marked
                            # with the 'preserve_snapshot' tag, delete it:
                            snaps_to_trim.append(snap)

                        # go on and look at the next snapshot,
                        #leaving the time period alone
                    else:
                        # this was the first snapshot found for this
                        #time period. Leave it alone and look at the
                        # next snapshot:
                        snap_found_for_this_time_period = True
                    check_this_snap = False
                else:
                    # the snap is after the cutoff date. Check it
                    # against the next cutoff date
                    time_period_number += 1
                    snap_found_for_this_time_period = False

        # We want to make sure we're only sending back 1 copy of each snapshot to trim.
        return list(set(snaps_to_trim))

    @staticmethod
    def get_volume_snapshots(volume, all_snapshots):
        """ Filters out the snapshots for a given volume from the entire list of snapshots. """
        # Get this volume's specific snapshots
        vol_snaps = [s for s in all_snapshots if s.volume_id == volume.id]
        EbsSnapshotter.sort_snapshots(vol_snaps)
        return vol_snaps

    # Reason: disable pylint too-many-arguments because this is the API I want to expose.
    # Status: permanently disabled
    # pylint: disable=too-many-arguments
    def trim_snapshots(self, hourly_backups, daily_backups, weekly_backups, monthly_backups, dry_run=False):
        """ Finds expired snapshots given the number of hourly, daily, weekly and monthly backups
            to keep, then removes them.
        """

        all_expired_snapshots = []
        deleted_snapshots = []
        errors = []

        volumes = self.get_volumes_with_schedule(ALL_SCHEDULES)

        if len(volumes) == 0:
            # Early exit for any region that doesn't have snapshotable volumes
            return (all_expired_snapshots, deleted_snapshots, errors)

        all_snapshots = self.ec2.get_all_snapshots()

        self.verbose_print("Removing snapshots for:", prefix="  ")

        for volume in volumes:
            vol_snaps = EbsSnapshotter.get_volume_snapshots(volume, all_snapshots)

            self.print_volume(volume, prefix="    ")

            self.print_snapshots(vol_snaps, msg="All Snapshots (%d):" % len(vol_snaps), prefix="      ")
            self.verbose_print()

            expired_snapshots = EbsSnapshotter.get_expired_snapshots(vol_snaps, hourly_backups, \
                                                                     daily_backups, weekly_backups, \
                                                                     monthly_backups)

            # We're going to return all of the expired snaps
            all_expired_snapshots.extend(expired_snapshots)

            self.print_snapshots(expired_snapshots, \
                                 msg="Expired Snapshots (%d):" % len(expired_snapshots), prefix="      ")
            self.verbose_print()

            self.verbose_print("Removing snapshots (%d):" % len(expired_snapshots), prefix="      ")

            # actually remove expired snapshots
            for exp_snap in expired_snapshots:
                self.verbose_print(exp_snap.id, prefix="        ")
                try:
                    if dry_run:
                        self.print_dry_run_msg(prefix="          ")
                    else:
                        exp_snap.delete()
                        deleted_snapshots.append(exp_snap)
                # Reason: disable pylint broad-except because we want to continue on error.
                # Status: permanently disabled
                # pylint: disable=broad-except
                except Exception as ex:
                    if isinstance(ex, EC2ResponseError) and ex.error_code == "InvalidSnapshot.NotFound":
                        # This message means that the snapshot is gone, which is what we
                        # were trying to do anyway. So, count this snap among the deleted.
                        deleted_snapshots.append(exp_snap)
                    else:
                        errors.append(ex)
                self.verbose_print()

        self.verbose_print("Number of expired snapshots: %d" % len(all_expired_snapshots), prefix="  ")
        self.verbose_print("Number of snapshots deleted: %d" % len(deleted_snapshots), prefix="  ")
        self.verbose_print("Number of snapshot deletion errors: %d" % len(errors), prefix="  ")
        self.verbose_print()

        return (all_expired_snapshots, deleted_snapshots, errors)
