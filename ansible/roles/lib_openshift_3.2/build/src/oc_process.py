# pylint: skip-file

class OCProcess(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    # pylint allows 5. we need 6
    # pylint: disable=too-many-arguments
    def __init__(self,
                 namespace,
                 tname=None,
                 params=None,
                 create=False,
                 kubeconfig='/etc/origin/master/admin.kubeconfig',
                 verbose=False):
        ''' Constructor for OpenshiftOC '''
        super(OCProcess, self).__init__(namespace, kubeconfig)
        self.namespace = namespace
        self.name = tname
        self.params = params
        self.create = create
        self.kubeconfig = kubeconfig
        self.verbose = verbose
        self._template = None

    @property
    def template(self):
        '''template property'''
        if self._template == None:
            results = self._process(self.name, False, self.params)
            if results['returncode'] != 0:
                raise OpenShiftCLIError('Error processing template [%s].' % self.name)
            self._template = results['results']['items']

        return self._template

    def get(self):
        '''get the template'''
        results = self._get('template', self.name)
        if results['returncode'] != 0:
            # Does the template exist??
            if 'not found' in results['stderr']:
                results['returncode'] = 0
                results['exists'] = False
                results['results'] = []

        return results

    def delete(self, obj):
        '''delete a resource'''
        return self._delete(obj['kind'], obj['metadata']['name'])

    def create_obj(self, obj):
        '''delete a resource'''
        return self._create_from_content(obj['metadata']['name'], obj)

    def process(self, create=None):
        '''process a template'''
        do_create = False
        if create != None:
            do_create = create
        else:
            do_create = self.create

        return self._process(self.name, do_create, self.params)

    def exists(self):
        '''return whether the template exists'''
        t_results = self._get('template', self.name)

        if t_results['returncode'] != 0:
            # Does the template exist??
            if 'not found' in t_results['stderr']:
                return False
            else:
                raise OpenShiftCLIError('Something went wrong. %s' % t_results)

        return True

    def needs_update(self):
        '''attempt to process the template and return it for comparison with oc objects'''
        obj_results = []
        for obj in self.template:

            # build a list of types to skip
            skip = []

            if obj['kind'] == 'ServiceAccount':
                skip.extend(['secrets', 'imagePullSecrets'])

             # fetch the current object
            curr_obj_results = self._get(obj['kind'], obj['metadata']['name'])
            if curr_obj_results['returncode'] != 0:
                # Does the template exist??
                if 'not found' in curr_obj_results['stderr']:
                    obj_results.append((obj, True))
                    continue

            # check the generated object against the existing object
            if not Utils.check_def_equal(obj, curr_obj_results['results'][0], skip_keys=skip):
                obj_results.append((obj, True))
                continue

            obj_results.append((obj, False))

        return obj_results

