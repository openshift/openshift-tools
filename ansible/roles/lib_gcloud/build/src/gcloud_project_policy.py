# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudProjectPolicy(GcloudCLI):
    ''' Class to wrap the gcloud compute iam service-accounts command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 project,
                 role=None,
                 member=None,
                 member_type='serviceAccount',
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudProjectPolicy, self).__init__(project=project)
        self._role = role
        self._member = '%s:%s' % (member_type, member)
        self._exist_policy = None
        self._policy_data = None
        self._policy_path = None
        self.verbose = verbose

    @property
    def existing_policy(self):
        '''existing project policy'''
        if self._exist_policy == None:
            results = self.list_project_policy()
            self._exist_policy = results['results']

        return self._exist_policy

    @property
    def member(self):
        '''property for member'''
        return self._member

    @property
    def role(self):
        '''property for role '''
        return self._role

    @property
    def policy_path(self):
        '''property for policy path'''
        return self._policy_path

    @policy_path.setter
    def policy_path(self, value):
        '''property for policy path'''
        self._policy_path = value

    @property
    def policy_data(self):
        '''property for policy data'''
        return self._policy_data

    @policy_data.setter
    def policy_data(self, value):
        '''property for policy data'''
        self._policy_data = value

    def list_project_policy(self):
        '''return project policy'''
        return self._list_project_policy(self.project)

    def remove_project_policy(self):
        ''' remove a member from a role in a project'''
        return self._remove_project_policy(self.project, self.member, self.role)

    def add_project_policy(self):
        '''create an service account key'''
        return self._add_project_policy(self.project, self.member, self.role)

    def set_project_policy(self, policy_data=None, policy_path=None):
        '''set a project policy '''
        # set the policy data and policy path
        self.convert_to_file(policy_data, policy_path)

        return self._set_project_policy(self.project, self.policy_path)

    def exists(self):
        '''check whether a member is in a project policy'''
        for policy in self.existing_policy['bindings']:
            if policy['role'] == self.role:
                return self.member in policy['members']

        return False

    def needs_update(self, policy_data=None, policy_path=None):
        '''compare results with incoming policy'''
        # set the policy data and policy path
        self.convert_to_file(policy_data, policy_path)

        for policy in self.policy_data['bindings']:
            for exist_policy in self.existing_policy['bindings']:
                if policy['role'] == exist_policy['role']:
                    if policy['members'] != exist_policy['members']:
                        return True
                    break
            else:
                # Did not find the role
                return True

        return False

    def convert_to_file(self, policy_data=None, policy_path=None):
        '''convert the policy data into a dict and ensure we have a file'''
        if policy_data:
            self.policy_data = policy_data
            self.policy_path = Utils.create_file('policy', policy_data, 'json')

        elif policy_path:
            self.policy_data = json.load(open(policy_path))
            self.policy_path = policy_path
