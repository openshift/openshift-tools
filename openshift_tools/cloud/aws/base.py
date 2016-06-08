# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is the base class for our AWS utility classes.
"""

import boto.ec2

# Specifically exclude certain regions
EXCLUDED_REGIONS = ['us-gov-west-1', 'cn-north-1']

DRY_RUN_MSG = "*** DRY RUN, NO ACTION TAKEN ***"

class Base(object):
    """ Class that provides base methods for other AWS utility classes """
    def __init__(self, region, verbose=False):
        """ Initialize the class """
        self.region = region
        self.ec2 = boto.ec2.connect_to_region(region)
        self.verbose = verbose

    def verbose_print(self, msg="", prefix="", end="\n"):
        """ Prints msg using prefix and end IF verbose is set on the class. """
        if self.verbose:
            print("%s%s%s") % (prefix, msg, end),

    def print_dry_run_msg(self, prefix="", end="\n"):
        """ Prints a dry run message. """
        self.verbose_print(DRY_RUN_MSG, prefix=prefix, end=end)

    @staticmethod
    def get_supported_regions():
        """ Returns the regions that we support (we're not allowed in all regions). """
        all_regions = boto.ec2.regions()

        supported_regions = [r for r in all_regions if r.name not in EXCLUDED_REGIONS]
        return supported_regions

    def print_volume(self, volume, prefix=""):
        """ Prints out the details of the given volume. """
        self.verbose_print("%s:" % volume.id, prefix=prefix)
        self.verbose_print("  Tags:", prefix=prefix)

        for tag in volume.tags.iteritems():
            self.verbose_print("    %s: %s" % (tag[0], tag[1]), prefix=prefix)

    def print_snapshots(self, snapshots, msg=None, prefix=""):
        """ Prints out the details for the given snapshots. """
        if msg:
            self.verbose_print(msg, prefix=prefix)

        for snap in snapshots:
            self.verbose_print("  %s: start_time %s" % (snap.id, snap.start_time), prefix=prefix)

