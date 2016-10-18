# vim: expandtab:tabstop=4:shiftwidth=4

"""
 This is a library for AWS instance utility methods.
"""


from openshift_tools.cloud.aws.base import Base

class InstanceUtil(Base):
    """ Useful utility methods for instances """

    def __init__(self, region, verbose=False):
        """ Initialize the class """
        super(InstanceUtil, self).__init__(region, verbose)

    def get_all_instances_as_dict(self):
        """ Returns a disctionary of all instances where the key is the instance id """
        retval = {}
        for inst in self.ec2.get_only_instances():
            retval[inst.id] = inst

        return retval
