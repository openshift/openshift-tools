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
module: statuspage_components
short_description: Create, modify, and idempotently manage statuspage components
description:
  - Manage statuspage components
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
    - Name of the component
    required: false
    default: None
    aliases: []
  status:
    description:
    - The status of the incident.
    choices: ['operational', 'degraged_performance', 'partial_outage', 'major_outage']
    required: false
    default: None
    aliases: []
  description:
    description:
    - The componnent description
    required: false
    default: None
    aliases: []
  group_name:
    description:
    - The name of the group this component is a part of
    required: false
    default: None
    aliases: []
'''

EXAMPLES = '''
# list indicents
  - name: list components
    statuspage_component:
      state: list
      api_key: "{{ api_key }}"
      org_id: "{{ org_id }}"
      page_id: "{{ page_id }}"
    register: incout

# create a component
  - name: create a component
    statuspage_component:
      state: present
      api_key: "{{ api_key }}"
      org_id: "{{ org_id }}"
      page_id: "{{ page_id }}"
      name: DNS
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

def main():
    '''
    ansible module for statuspage components
    '''

    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(default=os.environ.get('STATUSPAGE_API_KEY', ''), type='str'),
            page_id=dict(default=None, type='str', required=True, ),
            org_id=dict(default=None, type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            name=dict(default=None, type='str'),
            description=dict(default=None, type='str'),
            group_name=dict(default=None, type='str'),
            status=dict(default='operational', chioces=["operational", "degraded_performance",
                                                        "partial_outage", "major_outage"],
                        type='str'),
            verbose=dict(default=False, type='bool'),
        ),
        supports_check_mode=True,
    )

    results = StatusPageComponent.run_ansible(module.params)
    module.exit_json(**results)

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
if __name__ == '__main__':
    from ansible.module_utils.basic import *
    main()
