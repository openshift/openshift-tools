# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class OCEnv(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    container_path = {"pod": "spec#containers[0]#env",
                      "dc":  "spec#template#spec#containers[0]#env",
                      "rc":  "spec#template#spec#containers[0]#env",
                     }

    # pylint allows 5. we need 6
    # pylint: disable=too-many-arguments
    def __init__(self,
                 namespace,
                 kind,
                 env_vars,
                 resource_name=None,
                 list_all=False,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OpenshiftOC '''
        super(OCEnv, self).__init__(namespace, kubeconfig)
        self.kind = kind
        self.name = resource_name
        self.namespace = namespace
        self.list_all = list_all
        self.env_vars = env_vars
        self.kubeconfig = kubeconfig
        self.verbose = verbose
        self._yed = None

    @property
    def yed(self):
        ''' property function for yed var'''
        if not self._yed:
            self.get()
        return self._yed

    @yed.setter
    def yed(self, data):
        ''' setter function for yed var'''
        self._yed = data

    # pylint: disable=no-member
    def add_value(self, key, value):
        ''' add key, value pair to env array '''
        env = self.yed.get(OCEnv.container_path[self.kind])
        if env:
            env.append({'name': key, 'value': value})
        else:
            self.yed.put(OCEnv.container_path[self.kind], {'name': key, 'value': value})

    def value_exists(self, key, value):
        ''' return whether a key, value  pair exists '''
        results = self.yed.get(OCEnv.container_path[self.kind]) or []
        if not results:
            return False

        for result in results:
            if result['name'] == key and result['value'] == value:
                return True

        return False

    def key_exists(self, key):
        ''' return whether a key, value  pair exists '''
        results = self.yed.get(OCEnv.container_path[self.kind]) or []
        if not results:
            return False

        for result in results:
            if result['name'] == key:
                return True

        return False


    def get(self):
        '''return a environment variables '''
        env = self._get(self.kind, self.name)
        if env['returncode'] == 0:
            self.yed = Yedit(content=env['results'][0])
            env['results'] = self.yed.get(OCEnv.container_path[self.kind]) or []
        return env

    def delete(self):
        '''return all pods '''
        env = self.get()
        if env['returncode'] != 0:
            return env

        modified = False
        env_vars_array = self.yed.get(OCEnv.container_path[self.kind]) or []
        for key in self.env_vars.keys():
            idx = None
            for env_idx, env_var in enumerate(env_vars_array):
                if env_var['name'] == key:
                    idx = env_idx
                    break

            if idx:
                modified = True
                del env_vars_array[idx]


        #yed.put(OCEnv.container_path[self.kind], env_vars_array)
        if modified:
            return self._replace_content(self.kind, self.name, {OCEnv.container_path[self.kind]: env_vars_array})
        return {'returncode': 0, 'changed': False}


    # pylint: disable=too-many-function-args
    def put(self):
        '''place env vars into dc '''
        for update_key, update_value in self.env_vars.items():
            for var in self.yed.get(OCEnv.container_path[self.kind]):
                if update_key == var['name']:
                    var['value'] = update_value
                    break
            else:
                self.add_value(update_key, update_value)

        return self._replace_content(self.kind, self.name, self.yed.yaml_dict)

