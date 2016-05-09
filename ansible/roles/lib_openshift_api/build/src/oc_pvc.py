# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCPVC(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    kind = 'pvc'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(OCPVC, self).__init__(config.namespace, config.kubeconfig)
        self.config = config
        self.namespace = config.namespace
        self._pvc = None

    @property
    def pvc(self):
        ''' property function pvc'''
        if not self._pvc:
            self.get()
        return self._pvc

    @pvc.setter
    def pvc(self, data):
        ''' setter function for yedit var '''
        self._pvc = data

    def bound(self):
        '''return whether the pvc is bound'''
        if self.pvc.get_volume_name():
            return True

        return False

    def exists(self):
        ''' return whether a pvc exists '''
        if self.pvc:
            return True

        return False

    def get(self):
        '''return pvc information '''
        result = self._get(self.kind, self.config.name)
        if result['returncode'] == 0:
            self.pvc = PersistentVolumeClaim(content=result['results'][0])
        elif '\"%s\" not found' % self.config.name in result['stderr']:
            result['returncode'] = 0
            result['results'] = [{}]

        return result

    def delete(self):
        '''delete the object'''
        return self._delete(self.kind, self.config.name)

    def create(self):
        '''create the object'''
        return self._create_from_content(self.config.name, self.config.data)

    def update(self):
        '''update the object'''
        # need to update the tls information and the service name
        return self._replace_content(self.kind, self.config.name, self.config.data)

    def needs_update(self):
        ''' verify an update is needed '''
        if self.pvc.get_volume_name() or self.pvc.is_bound():
            return False

        skip = []
        return not Utils.check_def_equal(self.config.data, self.pvc.yaml_dict, skip_keys=skip, debug=True)
