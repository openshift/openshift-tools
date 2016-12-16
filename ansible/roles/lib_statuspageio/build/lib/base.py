# pylint: skip-file
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

