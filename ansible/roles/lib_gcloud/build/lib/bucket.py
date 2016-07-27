# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class Bucket(GCPResource):
    '''Object to represent a gcp storage bucket'''

    resource_type = "storage.v1.bucket"

    # pylint: disable=too-many-arguments
    def __init__(self, rname, project, zone):
        '''constructor for gcp resource'''
        super(Bucket, self).__init__(rname, Bucket.resource_type, project, zone)

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': Bucket.resource_type,
                'properties': {'name': self.name}
               }

