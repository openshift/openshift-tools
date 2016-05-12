# vim: expandtab:tabstop=4:shiftwidth=4
# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCGroup(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    kind = 'group'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 verbose=False):
        ''' Constructor for OCGroup '''
        super(OCGroup, self).__init__(config.namespace, config.kubeconfig)
        self.config = config
        self.namespace = config.namespace
        self._group = None

    @property
    def group(self):
        ''' property function service'''
        if not self._group:
            self.get()
        return self._group

    @group.setter
    def group(self, data):
        ''' setter function for yedit var '''
        self._group = data

    def exists(self):
        ''' return whether a group exists '''
        if self.group:
            return True

        return False

    def get(self):
        '''return group information '''
        result = self._get(self.kind, self.config.name)
        if result['returncode'] == 0:
            self.group = Group(content=result['results'][0])
        elif 'groups \"%s\" not found' % self.config.name in result['stderr']:
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
        skip = []
        return not Utils.check_def_equal(self.config.data, self.group.yaml_dict, skip_keys=skip, debug=True)
