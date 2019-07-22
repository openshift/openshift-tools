# vim: expandtab:tabstop=4:shiftwidth=4

#
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

"""simplezabbix Module
The purpose of this module is to give a simple interface into zabbix utilizing
the existing Ansible zabbix modules.
"""

import json
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C


class ResultsCallback(CallbackBase):
    ''' This class is simply a place to receive the ansible playbook
        run results '''
    def __init__(self):
        super(ResultsCallback, self).__init__()
        self.result = None
        self.raw_result = None
    def v2_runner_on_ok(self, result):
        ''' Store the result of the play '''
        self.result = result
        # want to store the raw json response details
        # pylint: disable=protected-access
        self.raw_result = result._result

class InputException(Exception):
    """Used when the input for an operation isn't what is expected.
    """
    pass

class ResultsException(Exception):
    """Used when the results of an operation aren't what was expected.
    """
    pass

class SimpleZabbixRaw(object):
    """A raw interface into the zbxapi using the Ansible Python API.

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

        {
            "invocation": {
                "module_name": "zbx_host",
                "module_args": {
                    "hostgroup_names": [
                        "Linux servers"
                    ],
                    "zbx_user": "Admin",
                    "name": "9597190206ab",
                    "template_names": [
                        "Template Heartbeat",
                        "Template Zagg Server"
                    ],
                    "state": "present",
                    ...
                }
            },
            "state": "present",
            "changed": false,
            "results": {
                ...
                "hostid": "10098",
                "name": "9597190206ab",
                "parentTemplates": [
                    {
                        "templateid": "10086"
                    },
                    {
                        "templateid": "10095"
                    }
                ],
                ...
            },
            "_ansible_no_log": false
        }

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

        {
            "invocation": {
                "module_name": "zbx_hostgroup",
                "module_args": {
                    "zbx_user": "Admin",
                    "name": "Linux servers",
                    ...
                }
            },
            "state": "present",
            "changed": false,
            "results": {
                "internal": "0",
                "flags": "0",
                "groupid": "2",
                "name": "Linux servers"
            },
            "_ansible_no_log": false
        }

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

        {
            "invocation": {
                "module_name": "zbx_template",
                "module_args": {
                    "zbx_user": "Admin",
                    "name": "Template Zagg Server",
                    ...
                }
            },
            "results": [
                {
                    "available": "0",
                    "groups": [
                        {
                            "groupid": "1"
                        }
                    ],
                    ...
                    "templateid": "10095",
                    "name": "Template Zagg Server",
                    ...
                }
            ],
            "_ansible_no_log": false
        }

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
        """Actually build an run an ansible play and return the results"""
        zclass = args.pop('zbx_class')

        # The leadup to the TaskQueueManager() call below is
        # copy pasted from Ansible's example:
        # https://docs.ansible.com/ansible/developing_api.html#python-api-2-0
        # pylint: disable=invalid-name
        Options = namedtuple('Options', ['connection', 'module_path',
                                         'forks', 'become', 'become_method',
                                         'become_user', 'check', 'diff'])

        loader = DataLoader()
        options = Options(connection='local', module_path=None,
                          forks=1, become=None,
                          become_method=None, become_user=None,
                          check=False, diff=False)
        passwords = dict(vault_pass='secret')

        results_callback = ResultsCallback()

        inventory = InventoryManager(loader=loader)
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        play_source = dict(name="Ansible Play",
                           hosts=self.pattern,
                           gather_facts='no',
                           tasks=[
                               dict(action=dict(module=zclass, args=args)),
                           ]
                          )

        play = Play().load(play_source, variable_manager=variable_manager,
                           loader=loader)

        tqm = None
        try:
            tqm = TaskQueueManager(inventory=inventory,
                                   variable_manager=variable_manager,
                                   loader=loader,
                                   options=options,
                                   passwords=passwords,
                                   stdout_callback=results_callback
                                  )
            return_code = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

            # Remove ansible tmpdir
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

        if return_code != 0:
            raise ResultsException("Ansible module run failed, no results given.")

        if results_callback.result.is_unreachable():
            message = "Ansible module run failed: module output:\n%s" % \
                      json.dumps(results_callback.raw_result, indent=4)
            raise ResultsException(message)

        if results_callback.result.is_failed():
            raise ResultsException(results_callback.raw_result)

        return results_callback.raw_result

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
        if result['results']:
           # If its a list, does the first result have a hostid?
            if isinstance(result['results'], list):
                if result['results'][0]['hostid']:
                    return True
           # If its a dict, does the result have hostids?
            if isinstance(result['results'], dict):
                if result['results'].has_key('hostids') or \
                   result['results'].has_key('hostid'):
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
        if result['results']:
           # If its a list, does the first result have a groupid?
            if isinstance(result['results'], list):
                if result['results'][0]['groupid']:
                    return True
           # If its a dict, does the result have groupids?
            if isinstance(result['results'], dict):
                if result['results'].has_key('groupid') or \
                   result['results'].has_key('groupids'):
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
        if result['results']:
           # If its a list, does the first result have a templateid?
            if isinstance(result['results'], list):
                if result['results'][0]['templateid']:
                    return True
           # If its a dict, does the result have templateids?
            if isinstance(result['results'], dict):
                if result['results'].has_key('templateids') or \
                   result['results'].has_key('templateid'):
                    return True

        return False # something went wrong
