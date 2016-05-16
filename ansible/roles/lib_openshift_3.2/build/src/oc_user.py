# vim: expandtab:tabstop=4:shiftwidth=4
# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCUser(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    kind = 'users'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 groups=None,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(OCUser, self).__init__(config.namespace, config.kubeconfig)
        self.config = config
        self.groups = groups
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

    def create_group_entries(self):
        ''' make entries for user to the provided group list '''
        if self.groups != None:
            for group in self.groups:
                cmd = ['groups', 'add-users', group, self.config.username]
                rval = self.openshift_cmd(cmd, oadm=True)
                if rval['returncode'] != 0:
                    return rval

                return rval

        return {'returncode': 0}

    def create(self):
        '''create the object'''
        rval = self.create_group_entries()
        if rval['returncode'] != 0:
            return rval

        return self._create_from_content(self.config.username, self.config.data)

    def group_update(self):
        ''' update group membership '''
        rval = {'returncode': 0}
        cmd = ['get', 'groups', '-n', self.namespace, '-o', 'json']
        all_groups = self.openshift_cmd(cmd, output=True)

        for group in all_groups['results']['items']:
            # If we're supposed to be in this group
            if group['metadata']['name'] in self.groups \
               and ( group['users'] == None or self.config.username not in group['users']):
                cmd = ['groups', 'add-users', group['metadata']['name'],
                       self.config.username]
                rval = self.openshift_cmd(cmd, oadm=True)
                if rval['returncode'] != 0:
                    return rval
            # else if we're in the group, but aren't supposed to be
            elif self.config.username in group['users'] \
                 and group['metadata']['name'] not in self.groups:
                cmd = ['groups', 'remove-users', group['metadata']['name'],
                       self.config.username]
                rval = self.openshift_cmd(cmd, oadm=True)
                if rval['returncode'] != 0:
                    return rval

        return rval

    def update(self):
        '''update the object'''
        rval = self.group_update()
        if rval['returncode'] != 0:
            return rval

        # need to update the user's info
        return self._replace_content(self.kind, self.config.username, self.config.data, force=True)

    def needs_group_update(self):
        ''' check if there are group membership changes '''
        cmd = ['get', 'groups', '-n', self.namespace, '-o', 'json']
        all_groups = self.openshift_cmd(cmd, output=True)
        for group in all_groups['results']['items']:
            # If we're supposed to be in this group
            if group['metadata']['name'] in self.groups \
               and ( group['users'] == None or self.config.username not in group['users']):
                return True
            # else if we're in the group, but aren't supposed to be
            elif self.config.username in group['users'] \
                 and group['metadata']['name'] not in self.groups:
                return True
        
        return False

    def needs_update(self):
        ''' verify an update is needed '''
        skip = []
        if self.needs_group_update() == True:
            return True

        return not Utils.check_def_equal(self.config.data, self.user.yaml_dict, skip_keys=skip, debug=True)

