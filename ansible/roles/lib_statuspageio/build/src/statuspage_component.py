# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class StatusPageComponent(StatusPageIOAPI):
    ''' Class to wrap the oc command line tools '''
    kind = 'sa'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 api_key,
                 page_id,
                 name=None,
                 description=None,
                 group_name=None,
                 status='operational',
                 org_id=None,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(StatusPageComponent, self).__init__(api_key, page_id, org_id)
        self.name = name
        self.status = status
        self.description = description
        self.group_name = group_name
        self.api_key = api_key
        self.page_id = page_id
        self.org_id = org_id
        self.verbose = verbose
        self._all_components = None
        self._group_id = None
        self._params = self.build_params()

    @property
    def all_components(self):
        ''' proeprty for components '''
        if self._all_components == None:
            self._all_components = self._get_components()

        return self._all_components

    @property
    def params(self):
        ''' proeprty for params '''
        if self._params == None:
            self._params = self.build_params()

        return self._params

    @params.setter
    def params(self, data):
        ''' setter function for params'''
        self._params = data

    @property
    def group_id(self):
        ''' proeprty for group_id '''
        if self._group_id == None and self.group_name != None:
            self._group_id = self.find_component_by_name(self.group_name)

        return self._group_id

    def get(self):
        '''return incidents'''
        # unresolved?  unscheduled?
        if self.group_name:
            return self._get_components_by_group(self.group_name)

        if self.name:
            return self._get_components_by_name([self.name])

        return self._get_components()

    def delete(self):
        '''delete the incident'''
        found = self.find_component()
        if len(found) == 1:
            return self._delete_component(found[0].id)

        return False

    def build_params(self):
        '''build parameters for update or create'''
        args = {'name': self.name,
                'description': self.description,
                'group_id': self.group_id,
                'status': self.status,
               }

        return args

    def update(self):
        '''update a component's status'''
        found = self.find_component()
        return self._update_component(found[0].id, name=self.name, desc=self.description, status=self.status)

    def create(self):
        '''create the object'''
        return self._create_component(self.params)

    def find_component_by_id(self, cid):
        '''return a component'''
        if cid == None:
            return None

        for comp in self.all_components:
            if cid == comp.id:
                return comp

        return None

    def find_component_by_name(self, name, group_name=None):
        '''return a component id'''
        ids = []
        for comp in self.all_components:
            if name == comp.name:
                # component does not have subcomponents and is either a group or main component
                if group_name == None and comp.group_id == None:
                    ids.append(comp.id)

                # component is a subcomponent and parent name needs to match group_name
                if group_name != None and comp.group_id == self.group_id:
                    ids.append(comp.id)

        if len(ids) == 1:
            return ids[0]

        raise StatusPageIOAPIError('Found %s instances matching your component name. ' \
                                   'Please specify a group name. ids=[%s].' \
                                   % (len(ids), ', '.join([cid for cid in ids])))


    def find_component(self):
        '''attempt to match the incoming component with existing components'''
        found = []
        for comp in self.all_components:
            if comp.name == self.params['name'] and \
               comp.group_id == self.group_id:

                # This could be the one!
                found.append(comp)

        return found

    def exists(self):
        ''' verify if the incoming component exists

            A component is unique by its name and by its group_id.
        '''
        found = self.find_component()

        if len(found) == 1:
            return True

        if len(found) == 0:
            return False

        raise StatusPageIOAPIError('Found %s instances matching your search. ' \
                                   ' Please resolve this issue ids=[%s].' \
                                   % (len(found), ', '.join([comp.id for comp in found])))

    def needs_update(self):
        ''' verify an update is needed '''
        # we need to check to see if the current status metches what we are about to update
        found = self.find_component()

        comp = found[0]

        # the components have only a few properties.  Check them.
        if comp.name == self.name and \
           comp.description == self.description and \
           comp.group_id == self.group_id and \
           comp.status == self.status:
            return False

        return True

    @staticmethod
    def run_ansible(params):
        '''run the idempotent actions'''
        spio = StatusPageComponent(params['api_key'],
                                   params['page_id'],
                                   params['name'],
                                   params['description'],
                                   params['group_name'],
                                   params['status'],
                                   params['org_id'],
                                   params['verbose'])

        results = spio.get()
        if params['state'] == 'list':
            return {'changed': False, 'result': results}

        elif params['state'] == 'absent':
            if spio.exists():
                results = spio.delete()
                return {'changed': True, 'result': results}
            else:
                return {'changed': False, 'result': {}}

        elif params['state'] == 'present':

            if not spio.exists():
                results = spio.create()
                return {'changed': True, 'result': results}

            elif spio.needs_update():
                results = spio.update()
                return {'changed': True, 'result': results}

            return {'changed': False, 'result': results}
        raise StatusPageIOAPIError('Unsupported state: %s' % params['state'])
