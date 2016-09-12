# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a library for gcp instance utility methods.
"""

# pylint: disable=no-name-in-module
from openshift_tools.cloud.gcp.base import Base

# pylint: disable=too-many-public-methods
class InstanceUtil(Base):
    """ Useful utility methods for instances """

    def __init__(self, project, region, creds_path=None, verbose=False):
        """ Initialize the class """
        super(InstanceUtil, self).__init__(project, region, creds_path, verbose)
        self.instances = None

    def get_all_instances_as_dict(self):
        """ Returns a disctionary of all instances where the key is the instance name """
        retval = {}
        for inst in self.instances:
            retval[inst['name']] = inst

        return retval
