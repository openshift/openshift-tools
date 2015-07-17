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

    def get_template_info(self, templates):
        """Queries Zabbix to get template information.

        Args:
            templates: a list of template names to get information for.

        Returns:
            The raw ansible results dictionary.

            Example:
            {
                "dark": {},
                "contacted": {
                    "localhost": {
                        "invocation": {
                            "module_name": "zbxapi",
                            "module_args": ""
                        },
                        "state": "list",
                        "changed": false,
                        "results": [
                            {
                                [... SNIP ...]
                                "host": "Template Heartbeat",
                                "templateid": "10085",
                                [... SNIP ...]
                            },
                            {
                                [... SNIP ...]
                                "host": "Template Host",
                                "templateid": "10088",
                                [... SNIP ...]
                            }
                        ]
                    }
                }
            }
        """
        args = {
            'server': self.url,
            'user': self.user,
            'password': self.password,
            'zbx_class': 'Template',
            'state': 'list',
            'params': {
                'filter': {
                    'host': templates,
                }
            }
        }

        results = self._run_ansible(args)
        return results

    def get_hostgroup_info(self, hostgroups):
        """Queries Zabbix to get hostgroup information.

        Args:
            hostgroups: a list of hostgroups to get information for.

        Returns:
            The raw ansible results dictionary.

            Example:
            {
                "dark": {},
                "contacted": {
                    "localhost": {
                        "invocation": {
                            "module_name": "zbxapi",
                            "module_args": ""
                        },
                        "state": "list",
                        "changed": false,
                        "results": [
                            {
                                "internal": "0",
                                "flags": "0",
                                "groupid": "2",
                                "name": "Linux servers"
                            },
                            {
                                "internal": "0",
                                "flags": "0",
                                "groupid": "6",
                                "name": "Virtual machines"
                            }
                        ]
                    }
                }
            }
        """
        args = {
            'server': self.url,
            'user': self.user,
            'password': self.password,
            'zbx_class': 'Hostgroup',
            'state': 'list',
            'params': {
                'filter': {
                    'name': hostgroups,
                }
            }
        }

        results = self._run_ansible(args)
        return results

    def ensure_host_is_present(self, name, tids, hgids, interfaces=None):
        """Ensures a host entry is present in zabbix.

        Args:
            name: the name of the host in zabbix
            tids: a list of template ids
            hgids: a list of hostgroup ids
            interfaces: optional interfaces definition

        Returns:
            The raw ansible results dictionary.

            Example:
            {
                "dark": {},
                "contacted": {
                    "localhost": {
                        "invocation": {
                            "module_name": "zbxapi",
                            "module_args": ""
                        },
                        "state": "present",
                        "changed": true,
                        "results": {
                            "jsonrpc": "2.0",
                            "result": {
                                "hostids": [
                                    "10112"
                                ]
                            },
                            "id": 1
                        }
                    }
                }
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
            'server': self.url,
            'user': self.user,
            'password': self.password,
            'zbx_class': 'Host',
            'state': 'present',
            'params': {
                'host': name,
                'interfaces': interfaces,
                'groups': hgids,
                'templates': tids,
                'output': 'extend',
                'filter': {
                    'host': [name],
                },
                'selectGroups': ['groupids'],
                'selectParentTemplates': ['templateids'],
            },
            'ignore': ['interfaces'],
        }

        results = self._run_ansible(args)
        return results

    def _run_ansible(self, args):
        """Actually make the call to the ansible runner."""
        results = ansible.runner.Runner(
            forks=1,
            pattern=self.pattern,
            transport='local',
            module_name='zbxapi',
            complex_args=args,
        ).run()

        if not results:
            raise ResultsException("Ansible module run failed, no results given.")

        if not results['contacted']:
            message = "Ansible module run failed: module output:\n%s" % \
                      json.dumps(results, indent=4)
            raise ResultsException(message)

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

    def get_template_ids(self, templates):
        """Queries Zabbix to get template IDs.

        Args:
            templates: a list of templates to get IDs for.

        Returns:
            A list of template IDs.

            Example: [u'10085', u'10088']
        """
        results = self.raw.get_template_info(templates)
        ids = [r['templateid'] for r in results['contacted'][self.raw.pattern]['results']]

        if not ids:
            raise ResultsException("Unable to convert template names into template IDs: %s" % templates)

        return ids

    def get_hostgroup_ids(self, hostgroups):
        """Queries Zabbix to get hostgroup IDs.

        Args:
            hostgroups: a list of hostgroups to get IDs for.

        Returns:
            A list of hostgroup IDs.

            Example: [u'2', u'6']
        """
        results = self.raw.get_hostgroup_info(hostgroups)
        ids = [r['groupid'] for r in results['contacted'][self.raw.pattern]['results']]

        if not ids:
            raise ResultsException("Unable to convert hostgroup names into hostgroup IDs: %s" % hostgroups)

        return ids

    def ensure_host_is_present(self, name, templates, hostgroups):
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
            The a boolean:
                True: the host is present and configured.
                False: an error occurred.

            Example:
            {
                "dark": {},
                "contacted": {
                    "localhost": {
                        "invocation": {
                            "module_name": "zbxapi",
                            "module_args": ""
                        },
                        "state": "present",
                        "changed": true,
                        "results": {
                            "jsonrpc": "2.0",
                            "result": {
                                "hostids": [
                                    "10112"
                                ]
                            },
                            "id": 1
                        }
                    }
                }
            }
        """


        if not templates or not hostgroups:
            raise InputException("This call requires templates and hostgroups to be set")

        tids = self.get_template_ids(templates)
        hgids = self.get_hostgroup_ids(hostgroups)

        result = self.raw.ensure_host_is_present(name, tids, hgids)

        if result['contacted'][self.raw.pattern]['results'].has_key('result') and \
           result['contacted'][self.raw.pattern]['results']['result']['hostids'][0]:
            return True # we got a hostid back, so we're all good


        if result['contacted'][self.raw.pattern]['results'].has_key('hostids') and \
            result['contacted'][self.raw.pattern]['results']['hostids'][0]:
            return True # we got a hostid back, so we're all good

        return False # something went wrong
