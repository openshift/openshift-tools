# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class Disk(GCPResource):
    '''Object to represent a gcp disk'''

    resource_type = "compute.v1.disk"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 rname,
                 project,
                 zone,
                 size,
                 disk_type='pd-standard', #pd-ssd, local-ssd
                 persistent=True,
                 auto_delete=True,
                 boot=False,
                 device_name=None,
                 image=None,
                ):
        '''constructor for gcp resource'''
        super(Disk, self).__init__(rname,
                                   Disk.resource_type,
                                   project,
                                   zone)
        if persistent:
            self._persistent = 'PERSISTENT'
        else:
            self._persistent = 'SCRATCH'

        self._size = size
        self._boot = boot
        self._image = image
        self._device_name = device_name
        self._disk_type = disk_type
        self._disk_url = None
        self._auto_delete = auto_delete

    @property
    def persistent(self):
        '''property for resource if boot device is persistent'''
        return self._persistent

    @property
    def device_name(self):
        '''property for resource device name'''
        return self._device_name

    @property
    def boot(self):
        '''property for resource is a boot device'''
        return self._boot

    @property
    def image(self):
        '''property for resource image'''
        return self._image

    @property
    def disk_type(self):
        '''property for resource disk type'''
        return self._disk_type

    @property
    def disk_url(self):
        '''property for resource disk url'''
        if self._disk_url == None:
            self._disk_url = Utils.zonal_compute_url(self.project, self.zone, 'diskTypes', self.disk_type)
        return self._disk_url

    @property
    def size(self):
        '''property for resource disk size'''
        return self._size

    @property
    def auto_delete(self):
        '''property for resource disk auto delete'''
        return self._auto_delete

    def get_instance_disk(self):
        '''return in vminstance format'''
        return {'deviceName': self.device_name,
                'type': self.persistent,
                'autoDelete': self.auto_delete,
                'boot': self.boot,
                'sizeGb': self.size,
                'initializeParams': {'diskName': self.name,
                                     'sourceImage': Utils.global_compute_url(self.project,
                                                                             'images',
                                                                             self.image)
                                    }
               }

    def get_supplement_disk(self):
        '''return in vminstance format'''
        return {'deviceName': self.device_name,
                'type': self.persistent,
                'source': '$(ref.%s.selfLink)' % self.name,
                'autoDelete': self.auto_delete,
               }

    def to_resource(self):
        """ return the resource representation"""
        return {'name': self.name,
                'type': Disk.resource_type,
                'properties': {'zone': self.zone,
                               'sizeGb': self.size,
                               'type': self.disk_url,
                               'autoDelete': self.auto_delete,
                              }
               }

