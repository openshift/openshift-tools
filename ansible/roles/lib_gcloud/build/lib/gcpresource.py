# pylint: skip-file

class GCPResource(object):
    '''Object to represent a gcp resource'''

    def __init__(self, rname, rtype, project, zone):
        '''constructor for gcp resource'''
        self._name = rname
        self._type = rtype
        self._project = project
        self._zone = zone

    @property
    def name(self):
        '''property for name'''
        return self._name

    @property
    def type(self):
        '''property for type'''
        return self._type

    @property
    def project(self):
        '''property for project'''
        return self._project

    @property
    def zone(self):
        '''property for zone'''
        return self._zone
