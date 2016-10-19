# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class StatusPageIncident(StatusPageIOAPI):
    ''' Class to wrap the oc command line tools '''
    kind = 'sa'

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 api_key,
                 page_id,
                 name=None,
                 scheduled=None,
                 unresolved=None,
                 org_id=None,
                 incident_type='realtime',
                 status='investigating',
                 update_twitter=False,
                 message=None,
                 components=None,
                 scheduled_for=None,
                 scheduled_until=None,
                 scheduled_remind_prior=False,
                 scheduled_auto_in_progress=False,
                 scheduled_auto_completed=False,
                 verbose=False):
        ''' Constructor for OCVolume '''
        super(StatusPageIncident, self).__init__(api_key, page_id, org_id)
        self.name = name
        self.api_key = api_key
        self.page_id = page_id
        self.org_id = org_id
        self.scheduled = scheduled
        self.unresolved = unresolved
        self.verbose = verbose
        self.incidents = None
        self.incident_type = incident_type
        self.status = status
        self.update_twitter = update_twitter
        self.message = message
        self.components = components
        self.scheduled_for = scheduled_for
        self.scheduled_until = scheduled_until
        self.scheduled_remind_prior = scheduled_remind_prior
        self.scheduled_auto_in_progress = scheduled_auto_in_progress
        self.scheduled_auto_completed = scheduled_auto_completed
        if self.components == None:
            self.components = {}
        self._params = None
        self._incidents = None

    @property
    def incidents(self):
        ''' property function service'''
        if not self._incidents:
            self._incidents = self.get()
        return self._incidents

    @incidents.setter
    def incidents(self, data):
        ''' setter function for incidents var '''
        self._incidents = data

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

    def get(self):
        '''return incidents'''
        # unresolved?  unscheduled?
        incs = self._get_incidents(scheduled=self.scheduled, unresolved_only=self.unresolved)
        if self.name:
            r_incs = []
            for inc in incs:
                if self.name.lower() in inc.name.lower():
                    r_incs.append(inc)
        else:
            r_incs = incs

        return r_incs

    def delete(self):
        '''delete the incident'''
        found, _, _ = self.find_incident()
        if len(found) == 1:
            results = self._delete_incident(found[0].id)
            for comp in found[0].incident_updates[-1].affected_components:
                self.set_component_status(comp.keys()[0], name=None, desc=None, status='operational')
            return results
        else:
            return False

    def build_params(self):
        '''build parameters for update or create'''
        ids = []
        r_comps = {}
        for inc_comp in self.components:
            if inc_comp.has_key('group') and inc_comp['group']:
                comps = self._get_components_by_group(inc_comp['group'])
            else:
                comps = self._get_components_by_name([_comp['name'] for _comp in inc_comp['component']])

            for comp in comps:
                # only include the components in my passed in component list
                if comp.name in [tmp_comp['name'] for tmp_comp in inc_comp['component']]:
                    ids.append(comp.id)
                    r_comps[comp.id] = comp

        if self.components and not ids:
            raise StatusPageIOAPIError('No components found.')

        args = {'name': self.name,
                'component_ids': ids,
                'message': self.message,
                'wants_twitter_update': self.update_twitter,
               }

        if self.status:
            args['status'] = self.status

        if self.incident_type == 'scheduled':
            args['scheduled_for'] = self.scheduled_for
            args['scheduled_until'] = self.scheduled_until
            args['scheduled_remind_prior'] = self.scheduled_remind_prior
            args['scheduled_auto_in_progress'] = self.scheduled_auto_in_progress
            args['scheduled_auto_completed'] = self.scheduled_auto_completed


        return {'params': args, 'comps': r_comps}

    def set_component_status(self, cid, name=None, desc=None, status=None):
        '''update a component's status'''
        return self._update_component(cid, name=name, desc=desc, status=status)

    def create(self):
        '''create the object'''
        params = self.params['params']
        comps = self.prepare_component_status(self.params['comps'])
        scheduled = self.incident_type == 'scheduled'

        results = self._create_incident(params, scheduled=scheduled)
        for cid, comp in comps.items():
            self.set_component_status(cid, name=None, desc=None, status=comp.status)

        return results

    def prepare_component_status(self, comps):
        '''prepare the component status for update'''
        # for each group
        for inc_comp in self.components:
            # for each component in this group
            for tmp_comp in inc_comp['component']:

                for ex_comp in comps.values():
                    if tmp_comp['name'] == ex_comp.name and tmp_comp.get('status', 'operational') != ex_comp.status:
                        ex_comp.status = tmp_comp.get('status', 'operational')

        return comps

    def update(self):
        '''update the object'''
        # need to update the tls information and the service name
        found, params, comps = self.find_incident()

        results = self._update_incident(found[0].id, kwargs=params)

        comps = self.prepare_component_status(comps)

        for cid, comp in comps.items():
            self.set_component_status(cid, name=None, desc=None, status=comp.status)

        return results

    @staticmethod
    def get_affected_components(aff_comps):
        '''return a list of affected component ids'''
        ids = []
        if aff_comps and aff_comps.has_key('affected_components'):
            for comp in aff_comps['affected_components']:
                ids.append(comp.keys()[0])

        return ids

    def find_incident(self):
        '''attempt to match the incoming incident with existing incidents'''
        params = self.params['params']
        comps = self.params['comps']

        found = []
        for incident in self.incidents:
            if incident.name == params['name'] and \
               incident.resolved_at == None and \
               set(StatusPageIncident.get_affected_components(incident.incident_updates[-1])) == \
               set(params['component_ids']):

                # This could be the one!
                found.append(incident)

        return found, params, comps

    def exists(self):
        ''' verify if the incoming incident exists

            As per some discussion, this is a difficult task without
            a unique identifier on the incident.

            Decision:  If an incident exists, with the same components, and the components
               are in the same state as before then we can say with a small degree of
               confidenced that this is the correct incident referred to by the caller.
        '''
        found, _, _ = self.find_incident()

        if len(found) == 1:
            return True

        if len(found) == 0:
            return False

        raise StatusPageIOAPIError('Found %s instances matching your search. Please resolve this issue ids=[%s].' \
                                   % (len(found), ', '.join([inc.id for inc in found])))

    def needs_update(self):
        ''' verify an update is needed '''
        # cannot update historical
        if self.incident_type == 'historical':
            return False

        # we need to check to see if the current status metches what we are about to update
        found, params, comps = self.find_incident()

        # check incoming components status against existing
        curr_incident = found[0]
        # for each group
        for comp in self.components:
            if comp['component']:
                # for each component in a group
                for inc_comp in comp['component']:
                    # for each comp in the current existing incident
                    for ex_comp in comps.values():
                        if ex_comp.name == inc_comp['name']:
                            if ex_comp.status == inc_comp.get('status', 'operational'):
                                break
                            return True
                    # didn't find the component name in the existing compents, need to update
                    else:
                        return True

        # Checdk the message is the same
        if params['message'] != curr_incident.incident_updates[-1].body or  \
           params['status'] != curr_incident.incident_updates[-1].status:
            return True

        if self.incident_type == 'scheduled':
            if self.scheduled_for != params['scheduled_for'] or \
               self.scheduled_until != params['scheduled_until'] or \
               self.scheduled_remind_prior != params['scheduled_remind_prior'] or \
               self.scheduled_auto_in_progress != params['scheduled_auto_in_progress'] or \
               self.scheduled_auto_completed != params['scheduled_auto_completed']:
                return True

        return False

    @staticmethod
    def run_ansible(params):
        '''run the idempotent actions'''
        spio = StatusPageIncident(params['api_key'],
                                  params['page_id'],
                                  params['name'],
                                  params['scheduled_only'],
                                  params['unresolved_only'],
                                  params['org_id'],
                                  params['incident_type'],
                                  params['status'],
                                  params['update_twitter'],
                                  params['message'],
                                  params['components'],
                                  params['scheduled_for'],
                                  params['scheduled_until'],
                                  params['scheduled_remind_prior'],
                                  params['scheduled_auto_in_progress'],
                                  params['scheduled_auto_completed'],
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
