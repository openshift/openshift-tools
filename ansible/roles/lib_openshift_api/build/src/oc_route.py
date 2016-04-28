# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCRoute(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''
    kind = 'route'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(OCRoute, self).__init__(config.namespace, config.kubeconfig)
        self.config = config
        self.namespace = config.namespace
        self._route = None

    @property
    def route(self):
        ''' property function service'''
        if not self._route:
            self.get()
        return self._route

    @route.setter
    def route(self, data):
        ''' setter function for yedit var '''
        self._route = data

    def exists(self):
        ''' return whether a volume exists '''
        if self.route:
            return True

        return False

    def get(self):
        '''return volume information '''
        result = self._get(self.kind, self.config.name)
        if result['returncode'] == 0:
            self.route = Route(content=result['results'][0])

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
        return not Utils.check_def_equal(self.config.data, self.route.yaml_dict, skip_keys=skip, debug=True)

