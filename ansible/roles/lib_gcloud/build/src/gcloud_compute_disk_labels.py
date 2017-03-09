# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudComputeDisk(GcloudCLI):
    ''' Class to wrap the gcloud compute images command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 project,
                 zone,
                 disk_info,
                 credentials=None,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudComputeDisk, self).__init__(credentials, project)
        self.zone = zone
        self.disk_info = disk_info
        self.verbose = verbose

    def set_labels(self, labels=None):
        '''set the labels for a disk'''
        return self._set_disk_labels(self.project,
                                     self.zone,
                                     self.disk_info['name'],
                                     labels,
                                     self.disk_info['labelFingerprint'])

    def delete_labels(self):
        ''' remove labels from a disk '''
        return self.set_labels(labels={})

    def has_labels(self, labels):
        '''does disk have labels set'''
        if not self.disk_info.has_key('labels'):
            return False
        if len(self.disk_info['labels']) == 0:
            return False

        if len(labels.keys()) != len(self.disk_info['labels'].keys()):
            return False

        for key, val in labels.items():
            if not self.disk_info['labels'].has_key(key) or self.disk_info['labels'][key] != val:
                return False

        return True

    def __str__(self):
        '''to str'''
        return "GcloudComputeDisk: %s" % self.disk_info['name']

