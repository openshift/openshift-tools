#!/usr/bin/env python # pylint: disable=too-many-lines
''' Ansible module '''
#     ___ ___ _  _ ___ ___    _ _____ ___ ___
#    / __| __| \| | __| _ \  /_\_   _| __|   \
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|

# vim: expandtab:tabstop=4:shiftwidth=4

#   Copyright 2016 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#  Purpose: An ansible module to communicate with statuspageio.

DOCUMENTATION = '''
module: statuspage_incident
short_description: Create, modify, and idempotently manage statuspage incidents
description:
  - Manage statuspage incidents
options:
  api_key:
    description:
    - statuspage api key
    required: True
    default: os.environ.get('STATUSPAGE_API_KEY', '')
    aliases: []
  page_id:
    description:
    - The statuspage page
    required: True
    default: None
    aliases: []
  org_id:
    description:
    - Organization id for the user.  Required when modifying users.
    required: false
    default: None
    aliases: []
  state:
    description:
    - Whether to create, update, delete, or list the desired object
    required: True
    default: present
    aliases: []
  name:
    description:
    - Name of the incident
    required: false
    default: None
    aliases: []
  unresolved_only:
    description:
    - Filter the incidents on the unresolved_only
    required: false
    default: None
    aliases: []
  scheduled_only:
    description:
    - Filter the incidents on the scheduled_only
    required: false
    default: None
    aliases: []
  incident_type:
    description:
    - The type of incident to create.
    choices: ['realtime', 'scheduled', 'historical']
    required: false
    default: None
    aliases: []
  status:
    description:
    - The status of the incident.
    choices: ['investigating', 'identified', 'monitoring', 'resolved', 'scheduled', 'in_progress', 'verifying', 'completed']
    required: false
    default: None
    aliases: []
  update_twitter:
    description:
    - Whether to update the twitters
    required: false
    default: False
    aliases: []
  message:
    description:
    - The incident message that gets posted
    required: false
    default: 60
    aliases: []
  impact_override:
    description:
    - Whether update the impact
    choices: ['none', 'minor', 'major', 'critical']
    required: false
    default: True
    aliases: []
  components:
    description:
    - An array of the components
    required: false
    default: None
    aliases: []
  scheduled_for:
    description:
    - The date when the maintenance will start
    required: false
    default: None
    aliases: []
  scheduled_until:
    description:
    - The date when the maintenance will end
    required: false
    default: None
    aliases: []
  scheduled_remind_prior:
    description:
    - Whether to remind the subscribers that the maintenance will begin
    required: false
    default: None
    aliases: []
  scheduled_auto_in_progress:
    description:
    - Whether to auto start the maintenance period and transition the status to in_progress
    required: false
    default: None
    aliases: []
  scheduled_auto_completed:
    description:
    - Whether to auto complete the maintenance period and transition the status to completed
    required: false
    default: None
    aliases: []
'''

EXAMPLES = '''
# list indicents
  - name: list incidents
    statuspage_incident:
      state: list
      api_key: "{{ api_key }}"
      org_id: "{{ org_id }}"
      page_id: "{{ page_id }}"
    register: incout

# create an incident
  - name: create an incident
    statuspage_incident:
      api_key: "{{ api_key }}"
      org_id: "{{ org_id }}"
      page_id: "{{ page_id }}"
      name: API Outage
      message: Investigating an issue with the API
      components:
      - group: opstest
        component:
        - name: Master API
          status: partial_outage
    register: incout
  - debug: var=incout

# create a scheduled maintenance incident
  - name: create a scheduled incident
    statuspage_incident:
      api_key: "{{ api_key }}"
      org_id: "{{ org_id }}"
      page_id: "{{ page_id }}"
      incident_type: scheduled
      status: scheduled
      name: Cluster upgrade
      message: "Upgrading from 3.2 to 3.3."
      components:
      - group: opstest
        component:
        - name: Etcd Service
          status: partial_outage
        - name: Master API
          status: partial_outage
      scheduled_for: '2016-10-14T13:21:00-0400'
      scheduled_until: '2016-10-14T13:25:00-0400'
      scheduled_auto_in_progress: True
	  scheduled_remind_prior: True
    register: incout
  - debug: var=incout

#resolve an incident
  - name: resolve an incident
    statuspage_incident:
      api_key: "{{ api_key }}"
      org_id: "{{ org_id }}"
      page_id: "{{ page_id }}"
      status: resolved
      name: API Outage
      message: "Fixed and ready to go."
      components:
      - group: opstest
        component:
        - name: Master API
          status: operational
    register: incout
  - debug: var=incout

'''
'''
   OpenShiftCLI class that wraps the oc commands in a subprocess
'''
# pylint: disable=too-many-lines

import os
# pylint: disable=import-error
import statuspageio

class StatusPageIOAPIError(Exception):
    '''Exception class for openshiftcli'''
    pass

# pylint: disable=too-few-public-methods
class StatusPageIOAPI(object):
    ''' Class to wrap the command line tools '''
    def __init__(self,
                 api_key,
                 page_id,
                 org_id=None):
        ''' Constructor for OpenshiftCLI '''
        self.api_key = api_key
        self.page_id = page_id
        self.org_id = org_id
        self.client = statuspageio.Client(api_key=self.api_key, page_id=self.page_id, organization_id=self.org_id)

    def _get_incidents(self, scheduled=False, unresolved_only=False):
        '''return a list of incidents'''
        if unresolved_only:
            return self.client.incidents.list_unresolved()

        if scheduled:
            return self.client.incidents.list_scheduled()

        return self.client.incidents.list()

    def _delete_component(self, compid):
        '''delete a component'''
        return self.client.components.delete(compid)

    def _delete_incident(self, incid):
        '''delete a incident'''
        return self.client.incidents.delete(incid)

    def _create_component(self, kwargs):
        '''create a component'''
        return self.client.components.create(**kwargs)


    def _create_incident(self, kwargs, scheduled=False):
        '''create a an incident'''
        if scheduled:
            return self.client.incidents.create_scheduled(**kwargs)

        return self.client.incidents.create(**kwargs)

    def _update_incident(self, incid, kwargs):
        '''return a list of incidents'''

        return self.client.incidents.update(incid, **kwargs)

    def _get_components_by_name(self, names):
        '''return the components in a specific group'''
        components = self._get_components()
        # first, find the parent component
        tmp_comps = []
        for comp in components:
            if comp.name in names:
                tmp_comps.append(comp)

        return tmp_comps

    def _get_components_by_group(self, group):
        '''return the components in a specific group'''
        components = self._get_components()
        # first, find the parent component
        tmp_comps = []
        parent = None
        for comp in components:
            if group == comp.name:
                parent = comp
                tmp_comps.append(comp)

        # now, find all subcomponents
        for comp in components:
            if comp.group_id == parent.id:
                tmp_comps.append(comp)

        return tmp_comps

    def _get_components(self):
        '''return components'''
        return self.client.components.list()

    def _update_component(self, cid, name=None, desc=None, status=None):
        '''update a component'''
        kwargs = {}
        if name:
            kwargs['name'] = name
        if desc:
            kwargs['desc'] = desc
        if status:
            kwargs['status'] = status

        return self.client.components.update(cid, **kwargs)


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

def main():
    '''
    ansible oc module for route
    '''

    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(default=os.environ.get('STATUSPAGE_API_KEY', ''), type='str'),
            page_id=dict(default=None, type='str', required=True, ),
            org_id=dict(default=None, type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            name=dict(default=None, type='str'),
            unresolved_only=dict(default=False, type='bool'),
            scheduled_only=dict(default=False, type='bool'),
            incident_type=dict(default='realtime', choices=['scheduled', 'realtime', 'historical'], type='str'),
            status=dict(default='investigating',
                        choices=['investigating', 'identified', 'monitoring', 'resolved',
                                 'scheduled', 'in_progress', 'verifying', 'completed'],
                        type='str'),
            update_twitter=dict(default=False, type='bool'),
            message=dict(default=None, type='str'),
            impact_override=dict(default=None, choices=['none', 'minor', 'major', 'critical'], type='str'),
            components=dict(default=None, type='list'),
            scheduled_for=dict(default=None, type='str'),
            scheduled_until=dict(default=None, type='str'),
            scheduled_remind_prior=dict(default=False, type='bool'),
            scheduled_auto_in_progress=dict(default=False, type='bool'),
            scheduled_auto_completed=dict(default=False, type='bool'),
            verbose=dict(default=False, type='bool'),
        ),
        supports_check_mode=True,
        required_if=[['incident_type', 'scheduled', ['scheduled_for', 'scheduled_until']]],
    )

    if module.params['incident_type'] == 'scheduled':
        if not module.params['status'] in ['scheduled', 'in_progress', 'verifying', 'completed']:
            module.exit_json(msg='If incident type is scheduled, then status must be one of ' +
                             'scheduled|in_progress|verifying|completed')

    elif module.params['incident_type'] in 'realtime':
        if not module.params['status'] in ['investigating', 'identified', 'monitoring', 'resolved']:
            module.exit_json(msg='If incident type is realtime, then status must be one of' +
                             ' investigating|identified|monitoring|resolved')


    results = StatusPageIncident.run_ansible(module.params)
    module.exit_json(**results)

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
if __name__ == '__main__':
    from ansible.module_utils.basic import *
    main()
