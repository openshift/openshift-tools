# vim: expandtab:tabstop=4:shiftwidth=4

#
#   Copyright 2015 Red Hat Inc.
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

"""simplezabbix Module
The purpose of this module is to give a simple interface into zabbix using the
Ansible Runner and the openshift-ansible zbxapi module.
"""

import ansible.runner
import json

class InputException(Exception):
    """Used when the input for an operation isn't what is expected.
    """
    pass

class ResultsException(Exception):
    """Used when the results of an operation aren't what was expected.
    """
    pass

class SimpleZabbixRaw(object):
    """A raw interface into the zbxapi and ansible runner calls.

    The purpose of this module is to be a lower level api. It returns exactly
    what ansible returns (no processing done, no evaluations made).
    """

    def __init__(self, url, user, password):
        """Contructs the object

        Args:
            url: the zabbix api URL (ex: http://localhost/zabbix/api_jsonrpc.php)
            user: the zabbix api user
            password: the zabbix api password
        """
        self.url = url
        self.user = user
        self.password = password

        # for now, we want to always run the zabbix module locally
        self.pattern = 'localhost'

    def ensure_host_exists(self, name, templates, hostgroups, interfaces=None):
        """Ensures a host entry is present in zabbix.

        Args:
            name: the name of the host in zabbix
            templates: a list of template names
            hostgroups: a list of hostgroup names
            interfaces: optional interfaces definition

        Returns:
            The raw ansible results dictionary.

            {'contacted': {'localhost': {u'changed': True,
                                         'invocation': {'module_args': '', 'module_name': 'zbx_host'},
                                         u'results': {u'hostids': [u'10093']},
                                         u'state': u'present'}},
             'dark': {}}

        """
        if not interfaces:
            interfaces = [
                {
                    'type': 1,
                    'main': 1,
                    'useip': 1,
                    'ip': '127.0.0.1',
                    'dns': '',
                    'port': 10050,
                }
            ]

        args = {
            'zbx_server': self.url,
            'zbx_user': self.user,
            'zbx_password': self.password,
            'zbx_class': 'zbx_host',
            'name': name,
            'interfaces': interfaces,
            'hostgroup_names': hostgroups,
            'template_names': templates,
        }

        results = self._run_ansible(args)
        return results

    def ensure_hostgroup_exists(self, name):
        """Ensures a hostgroup entry is present in zabbix.

        Args:
            name: the name of the hostgroup in zabbix

        Returns:
            The raw ansible results dictionary.

            {'contacted': {'localhost': {u'changed': False,
                                         'invocation': {'module_args': '', 'module_name': 'zbx_hostgroup'},
                                         u'results': {u'flags': u'0',
                                                      u'groupid': u'2',
                                                      u'internal': u'0',
                                                      u'name': u'Linux servers'},
                                         u'state': u'present'}},
             'dark': {}}

        """
        args = {
            'zbx_server': self.url,
            'zbx_user': self.user,
            'zbx_password': self.password,
            'zbx_class': 'zbx_hostgroup',
            'name': name,
        }

        results = self._run_ansible(args)
        return results

    def ensure_template_exists(self, name):
        """Ensures a template entry is present in zabbix.

        Args:
            name: the name of the template in zabbix

        Returns:
            The raw ansible results dictionary.

            {'contacted': {'localhost': {u'changed': False,
                             'invocation': {'module_args': '', 'module_name': 'zbx_template'},
                             u'results': [
                             "results": [{
                                 "jsonrpc": "2.0",
                                 "result": {
                                     "hostids": [
                                         "10112"
                                     ]
                                 },
                                 "id": 1
                             }]
                             u'state': u'present'}},
            'dark': {}}
        """
        args = {
            'zbx_server': self.url,
            'zbx_user': self.user,
            'zbx_password': self.password,
            'zbx_class': 'zbx_template',
            'name': name,
        }

        results = self._run_ansible(args)
        return results

    def _run_ansible(self, args):
        """Actually make the call to the ansible runner."""
        zclass = args.pop('zbx_class')
        results = ansible.runner.Runner(
            forks=1,
            pattern=self.pattern,
            transport='local',
            module_name=zclass,
            complex_args=args,
        ).run()

        if not results:
            raise ResultsException("Ansible module run failed, no results given.")

        if not results['contacted']:
            message = "Ansible module run failed: module output:\n%s" % \
                      json.dumps(results, indent=4)
            raise ResultsException(message)

        if results['contacted'].has_key('localhost') and results['contacted']['localhost'].has_key('msg'):
            raise ResultsException(results['contacted']['localhost'])

        return results

class SimpleZabbix(object):
    """A simple interface into the zbxapi and ansible runner calls.

    The purpose of this module is to be a higher level api. It returns
    simple data in normal python data structures. It's meant to address the
    90% simple cases. For the other 10% cases, use SimpleZabbixRaw or the
    Ansible runner interface directly.
    """
    def __init__(self, url, user, password):
        """Contructs the object

        Args:
            url: the zabbix api URL (ex: http://localhost/zabbix/api_jsonrpc.php)
            user: the zabbix api user
            password: the zabbix api password
        """
        self.raw = SimpleZabbixRaw(url, user, password)

    def ensure_host_exists(self, name, templates, hostgroups):
        """Ensures a host entry is present in zabbix.

        Note, this is an idempotent operation:
            if the host is present, and the same, nothing will be done
            if the host is present, but different, an attempt will be made to update it
            if the host is not present, it will be created.

        Args:
            name: the name of the host in zabbix
            templates: a list of templates the is linked to
            hostgroups: a list of hostgroups the host belongs to

        Returns:
            A boolean:
                True: the host is present and configured.
                False: an error occurred.

        """
        if not templates or not hostgroups:
            raise InputException("This call requires templates and hostgroups to be set")

        result = self.raw.ensure_host_exists(name, templates, hostgroups)

        # Results can be a list of results or can be a dictionary of the created object
        if result['contacted'][self.raw.pattern]['results']:
           # If its a list, does the first result have a hostid?
            if isinstance(result['contacted'][self.raw.pattern]['results'], list):
                if result['contacted'][self.raw.pattern]['results'][0]['hostid']:
                    return True
           # If its a dict, does the result have hostids?
            if isinstance(result['contacted'][self.raw.pattern]['results'], dict):
                if result['contacted'][self.raw.pattern]['results'].has_key('hostids') or \
                   result['contacted'][self.raw.pattern]['results'].has_key('hostid'):
                    return True


        return False # something went wrong

    def ensure_hostgroup_exists(self, name):
        """Ensures a hostgroup entry is present in zabbix.

        Note, this is an idempotent operation:
            if the hostgroup is present, and the same, nothing will be done
            if the hostgroup is present, but different, an attempt will be made to update it
            if the hostgroup is not present, it will be created.

        Args:
            name: the name of the hostgroup in zabbix

        Returns:
            A boolean:
                True: the hostgroup is present and configured.
                False: an error occurred.

        """
        if not name:
            raise InputException("This call requires name to be set")

        result = self.raw.ensure_hostgroup_exists(name)

        # Results can be a list of results or can be a dictionary of the created object
        if result['contacted'][self.raw.pattern]['results']:
           # If its a list, does the first result have a groupid?
            if isinstance(result['contacted'][self.raw.pattern]['results'], list):
                if result['contacted'][self.raw.pattern]['results'][0]['groupid']:
                    return True
           # If its a dict, does the result have groupids?
            if isinstance(result['contacted'][self.raw.pattern]['results'], dict):
                if result['contacted'][self.raw.pattern]['results'].has_key('groupid') or \
                   result['contacted'][self.raw.pattern]['results'].has_key('groupids'):
                    return True


        return False # something went wrong

    def ensure_template_exists(self, name):
        """Ensures a template entry is present in zabbix.

        Note, this is an idempotent operation:
            if the template is present, and the same, nothing will be done
            if the template is present, but different, an attempt will be made to update it
            if the template is not present, it will be created.

        Args:
            name: the name of the template in zabbix

        Returns:
            A boolean:
                True: the template is present and configured.
                False: an error occurred.

        """
        if not name:
            raise InputException("This call requires name to be set")

        result = self.raw.ensure_template_exists(name)

        # Results can be a list of results or can be a dictionary of the created object
        if result['contacted'][self.raw.pattern]['results']:
           # If its a list, does the first result have a templateid?
            if isinstance(result['contacted'][self.raw.pattern]['results'], list):
                if result['contacted'][self.raw.pattern]['results'][0]['templateid']:
                    return True
           # If its a dict, does the result have templateids?
            if isinstance(result['contacted'][self.raw.pattern]['results'], dict):
                if result['contacted'][self.raw.pattern]['results'].has_key('templateids') or \
                   result['contacted'][self.raw.pattern]['results'].has_key('templateid'):
                    return True

        return False # something went wrong
