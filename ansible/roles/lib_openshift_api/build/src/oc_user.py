# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCUser(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    kind = 'users'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(OCUser, self).__init__(config.namespace, config.kubeconfig)
        self.config = config
        self._user = None

    @property
    def user(self):
        ''' property function service'''
        if not self._user:
            self.get()
        return self._user

    @user.setter
    def user(self, data):
        ''' setter function for yedit var '''
        self._user = data

    def exists(self):
        ''' return whether a user exists '''
        if self.user:
            return True

        return False

    def get(self):
        '''return user information '''
        result = self._get(self.kind, self.config.username)
        if result['returncode'] == 0:
            self.user = User(content=result['results'][0])
        elif 'users \"%s\" not found' % self.config.username in result['stderr']:
            result['returncode'] = 0
            result['results'] = [{}]

        return result

    def delete(self):
        '''delete the object'''
        return self._delete(self.kind, self.config.username)

    def create(self):
        '''create the object'''
        return self._create_from_content(self.config.username, self.config.data)

    def update(self):
        '''update the object'''
        # need to update the user's info
        return self._replace_content(self.kind, self.config.username, self.config.data, force=True)

    def needs_update(self):
        ''' verify an update is needed '''
        skip = []
        return not Utils.check_def_equal(self.config.data, self.user.yaml_dict, skip_keys=skip, debug=True)

