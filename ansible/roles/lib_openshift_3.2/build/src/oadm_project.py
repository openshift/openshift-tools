# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OadmProject(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    kind = 'project'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(OadmProject, self).__init__(config.name, config.kubeconfig)
        self.config = config
        self._project = None

    @property
    def project(self):
        ''' property function project'''
        if not self._project:
            self.get()
        return self._project

    @project.setter
    def project(self, data):
        ''' setter function for yedit var '''
        self._project = data

    def exists(self):
        ''' return whether a project exists '''
        if self.project:
            return True

        return False

    def get(self):
        '''return project '''
        result = self.openshift_cmd(['get', self.kind, self.config.name, '-o', 'json'], output=True, output_type='raw')

        if result['returncode'] == 0:
            self.project = Project(content=json.loads(result['results']))
            result['results'] = self.project.yaml_dict

        elif 'namespaces "%s" not found' % self.config.name in result['stderr']:
            result = {'results': [], 'returncode': 0}

        return result

    def delete(self):
        '''delete the object'''
        return self._delete(self.kind, self.config.name)

    def create(self):
        '''create a project '''
        cmd = ['new-project', self.config.name]
        cmd.extend(self.config.to_option_list())

        return self.openshift_cmd(cmd, oadm=True)

    def update(self):
        '''update a project '''

        self.project.update_annotation('display-name', self.config.config_options['display_name']['value'])
        self.project.update_annotation('description', self.config.config_options['description']['value'])
        self.project.update_annotation('node-selector', self.config.config_options['node_selector']['value'])
        return self._replace_content(self.kind, self.config.namespace, self.project.yaml_dict)

    def needs_update(self):
        ''' verify an update is needed '''
        result = self.project.find_annotation("display-name")
        if result != self.config.config_options['display_name']['value']:
            return True

        result = self.project.find_annotation("desription")
        if result != self.config.config_options['description']['value']:
            return True

        result = self.project.find_annotation("node-selector")
        if result != self.config.config_options['node_selector']['value']:
            return True

        # Check rolebindings and policybindings
        return False

