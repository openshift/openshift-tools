#!/usr/bin/env python # pylint: disable=too-many-lines
''' zabbix module'''
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
#  Purpose: An ansible module to communicate with zabbix.
#  Requires Packages on python < 2.7.9:
#      python-pyasn1 python-ndg_httpsclient pyOpenSSL
#

DOCUMENTATION = '''
module: zbx_maintenance
short_description: Create, modify, and idempotently manage zabbix mainteance.
description:
  - Manage zabbix maintenances programmatically.
options:
  zbx_server:
    description:
    - zabbix server url
    required: false
    default: https://localhost/zabbix/api_jsonrpc.php
    aliases: []
  zbx_user:
    description:
    - zabbix server username
    required: false
    default: lookup env var named ZABBIX_USER or None
    aliases: []
  zbx_password:
    description:
    - zabbix server password
    required: false
    default: lookup env var named ZABBIX_PASSWORD or None
    aliases: []
  zbx_debug:
    description:
    - Turn on zabbix debug messages.
    required: false
    default: false
    aliases: []
  zbx_sslverify:
    description:
    - Turn on/off sslverification
    required: false
    default: false
    aliases: []
  state:
    description:
    - Whether to create, update, delete, or list the desired object
    required: false
    default: present
    aliases: []
  hosts:
    description:
    - A list of hosts to put into maintenance
    required: false
    default: None
    aliases: []
  hostgroups:
    description:
    - A list of hostgroups to put into maintenance
    required: false
    default: None
    aliases: []
  name:
    description:
    - Name of the zabbix maintenance
    required: false
    default: None
    aliases: []
  description:
    description:
    - Description of the zabbix maintenance
    required: false
    default: None
    aliases: []
  start_date:
    description:
    - The epoch representation of the start of the maintenance time
    required: false
    default: int(time.time())
    aliases: []
  duration:
    description:
    - The amount of time you want for maintenance in minutes
    required: false
    default: 60
    aliases: []
  data_collection:
    description:
    - Whether to collect data during the maintenance window
    required: false
    default: True
    aliases: []
'''

EXAMPLES = '''
# zabbix maintenance
  - name: create maintenance
    zbx_maintenance:
      zbx_server: 'https://localhost/zabbix/api_jsonrpc.php'
      zbx_user: Admin
      zbx_password: zabbix
      zbx_debug: False
      zbx_sslverify: True
      name: maintenance test
      description: testing my maintenance
      start_date: 1473861286
      duration: 15
      data_collection: False
      hostgroups:
      - Int Environment

# Env vars for user / pass and defaults for others
# lookup for epoch
# hosts passed as an array
  - name: create maintenance
    zbx_maintenance:
      zbx_server: 'https://localhost/zabbix/api_jsonrpc.php'
      name: maintenance test
      description: testing my maintenance
      start_date: "{{ lookup('pipe', 'date +%s') }}"
      duration: 15
      data_collection: False
      hosts:
      - host1
      - host2
# Note: when creating a maintenance with a variable for start_date it will
# continue to change when rerunning the module as the time will be different
# and require an update.
'''
import json
import requests
import httplib
import copy

class ZabbixAPIError(Exception):
    '''
        ZabbixAPIError
        Exists to propagate errors up from the api
    '''
    pass

# Disabling to have DTO
# pylint: disable=too-few-public-methods

# DTO needs an extra arg
# pylint: disable=too-many-arguments

class ZabbixConnection(object):
    '''
    Placeholder for connection options
    '''
    def __init__(self, server, username, password, ssl_verify=False, verbose=False):
        self.server = server
        self.username = username
        self.password = password
        self.verbose = verbose
        self.ssl_verify = ssl_verify

class ZabbixAPI(object):
    '''
        ZabbixAPI class
    '''
    # disabling for readability
    # pylint: disable=line-too-long
    classes = {
        'Action': ['create', 'delete', 'get', 'update'],
        'Alert': ['get'],
        'Application': ['create', 'delete', 'get', 'massadd', 'update'],
        'Configuration': ['export', 'import'],
        'Dhost': ['get'],
        'Dcheck': ['get'],
        'Discoveryrule': ['copy', 'create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Drule': ['copy', 'create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Dservice': ['get'],
        'Event': ['acknowledge', 'get'],
        'Graph': ['create', 'delete', 'get', 'update'],
        'Graphitem': ['get'],
        'Graphprototype': ['create', 'delete', 'get', 'update'],
        'History': ['get'],
        'Hostgroup': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'massadd', 'massremove', 'massupdate', 'update'],
        'Hostinterface': ['create', 'delete', 'get', 'massadd', 'massremove', 'replacehostinterfaces', 'update'],
        'Host': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'massadd', 'massremove', 'massupdate', 'update'],
        'Hostprototype': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Httptest': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Iconmap': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Image': ['create', 'delete', 'get', 'update'],
        'Item': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Itemprototype': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Maintenance': ['create', 'delete', 'get', 'update'],
        'Map': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Mediatype': ['create', 'delete', 'get', 'update'],
        'Proxy': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Screen': ['create', 'delete', 'get', 'update'],
        'Screenitem': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'update', 'updatebyposition'],
        'Script': ['create', 'delete', 'execute', 'get', 'getscriptsbyhosts', 'update'],
        'Service': ['adddependencies', 'addtimes', 'create', 'delete', 'deletedependencies', 'deletetimes', 'get', 'getsla', 'isreadable', 'iswritable', 'update'],
        'Template': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'massadd', 'massremove', 'massupdate', 'update'],
        'Templatescreen': ['copy', 'create', 'delete', 'get', 'isreadable', 'iswritable', 'update'],
        'Templatescreenitem': ['get'],
        'Trigger': ['adddependencies', 'create', 'delete', 'deletedependencies', 'get', 'isreadable', 'iswritable', 'update'],
        'Triggerprototype': ['create', 'delete', 'get', 'update'],
        'User': ['addmedia', 'create', 'delete', 'deletemedia', 'get', 'isreadable', 'iswritable', 'login', 'logout', 'update', 'updatemedia', 'updateprofile'],
        'Usergroup': ['create', 'delete', 'get', 'isreadable', 'iswritable', 'massadd', 'massupdate', 'update'],
        'Usermacro': ['create', 'createglobal', 'delete', 'deleteglobal', 'get', 'update', 'updateglobal'],
        'Usermedia': ['get'],
    }

    def __init__(self, zabbix_connection=None):
        self.server = zabbix_connection.server
        self.username = zabbix_connection.username
        self.password = zabbix_connection.password
        if any([value == None for value in [self.server, self.username, self.password]]):
            raise ZabbixAPIError('Please specify zabbix server url, username, and password.')

        self.verbose = zabbix_connection.verbose
        self.ssl_verify = zabbix_connection.ssl_verify
        if self.verbose:
            httplib.HTTPSConnection.debuglevel = 1
            httplib.HTTPConnection.debuglevel = 1
        self.auth = None

        for cname, _ in self.classes.items():
            setattr(self, cname.lower(), getattr(self, cname)(self))

        # pylint: disable=no-member
        # This method does not exist until the metaprogramming executed
        resp, content = self.user.login(user=self.username, password=self.password)

        if resp.status_code == 200:
            if content.has_key('result'):
                self.auth = content['result']
            elif content.has_key('error'):
                raise ZabbixAPIError("Unable to authenticate with zabbix server. {0} ".format(content['error']))
        else:
            raise ZabbixAPIError("Error in call to zabbix. Http status: {0}.".format(resp.status_code))

    def perform(self, method, rpc_params):
        '''
        This method calls your zabbix server.

        It requires the following parameters in order for a proper request to be processed:
            jsonrpc - the version of the JSON-RPC protocol used by the API;
                      the Zabbix API implements JSON-RPC version 2.0;
            method - the API method being called;
            rpc_params - parameters that will be passed to the API method;
            id - an arbitrary identifier of the request;
            auth - a user authentication token; since we don't have one yet, it's set to null.
        '''
        jsonrpc = "2.0"
        rid = 1

        headers = {}
        headers["Content-type"] = "application/json"

        body = {
            "jsonrpc": jsonrpc,
            "method":  method,
            "params":  rpc_params.get('params', {}),
            "id":      rid,
            'auth':    self.auth,
        }

        if method in ['user.login', 'api.version']:
            del body['auth']

        body = json.dumps(body)

        if self.verbose:
            print "BODY:", body
            print "METHOD:", method
            print "HEADERS:", headers

        request = requests.Request("POST", self.server, data=body, headers=headers)
        session = requests.Session()
        req_prep = session.prepare_request(request)
        response = session.send(req_prep, verify=self.ssl_verify)

        if response.status_code not in [200, 201]:
            raise ZabbixAPIError('Error calling zabbix.  Zabbix returned %s' % response.status_code)

        if self.verbose:
            print "RESPONSE:", response.text

        try:
            content = response.json()
        except ValueError as err:
            content = {"error": err.message}

        return response, content

    @staticmethod
    def meta(cname, method_names):
        '''
        This bit of metaprogramming is where the ZabbixAPI subclasses are created.
        For each of ZabbixAPI.classes we create a class from the key and methods
        from the ZabbixAPI.classes values.  We pass a reference to ZabbixAPI class
        to each subclass in order for each to be able to call the perform method.
        '''
        def meta_method(_class, method_name):
            '''
            This meta method allows a class to add methods to it.
            '''
            # This template method is a stub method for each of the subclass
            # methods.
            def template_method(self, params=None, **rpc_params):
                '''
                This template method is a stub method for each of the subclass methods.
                '''
                if params:
                    rpc_params['params'] = params
                else:
                    rpc_params['params'] = copy.deepcopy(rpc_params)

                return self.parent.perform(cname.lower()+"."+method_name, rpc_params)

            template_method.__doc__ = \
              "https://www.zabbix.com/documentation/2.4/manual/api/reference/%s/%s" % \
              (cname.lower(), method_name)
            template_method.__name__ = method_name
            # this is where the template method is placed inside of the subclass
            # e.g. setattr(User, "create", stub_method)
            setattr(_class, template_method.__name__, template_method)

        # This class call instantiates a subclass. e.g. User
        _class = type(cname,
                      (object,),
                      {'__doc__': \
                      "https://www.zabbix.com/documentation/2.4/manual/api/reference/%s" % cname.lower()})
        def __init__(self, parent):
            '''
            This init method gets placed inside of the _class
            to allow it to be instantiated.  A reference to the parent class(ZabbixAPI)
            is passed in to allow each class access to the perform method.
            '''
            self.parent = parent

        # This attaches the init to the subclass. e.g. Create
        setattr(_class, __init__.__name__, __init__)
        # For each of our ZabbixAPI.classes dict values
        # Create a method and attach it to our subclass.
        # e.g.  'User': ['delete', 'get', 'updatemedia', 'updateprofile',
        #                'update', 'iswritable', 'logout', 'addmedia', 'create',
        #                'login', 'deletemedia', 'isreadable'],
        # User.delete
        # User.get
        for method_name in method_names:
            meta_method(_class, method_name)
        # Return our subclass with all methods attached
        return _class

    def get_content(self, zbx_class_name, method, params):
        '''
        This bit of metaprogramming takes a zabbix_class_name (e.g. 'user' )
        This gets the instantiated object of type user and calls method
        with params as the parameters.

        Returns the zabbix query results
        '''
        zbx_class_inst = self.__getattribute__(zbx_class_name.lower())
        zbx_class = self.__getattribute__(zbx_class_name.capitalize())
        return zbx_class.__dict__[method](zbx_class_inst, params)[1]

# Attach all ZabbixAPI.classes to ZabbixAPI class through metaprogramming
for _class_name, _method_names in ZabbixAPI.classes.items():
    setattr(ZabbixAPI, _class_name, ZabbixAPI.meta(_class_name, _method_names))

# pylint: disable=line-too-long
# Disabling line length for readability

import os
import time
import datetime

class Utils(object):
    ''' zabbix utilities class'''


    @staticmethod
    def get_priority(priority):
        ''' determine priority '''
        prior = 0
        if 'info' in priority:
            prior = 1
        elif 'warn' in priority:
            prior = 2
        elif 'avg' == priority or 'ave' in priority:
            prior = 3
        elif 'high' in priority:
            prior = 4
        elif 'dis' in priority:
            prior = 5

        return prior

class Zbx(object):
    '''base class for zabbix modules'''

    def __init__(self,
                 zbx_server,
                 zbx_user,
                 zbx_password,
                 zbx_class_name,
                 zbx_class_id,
                 zbx_debug=False,
                 zbx_sslverify=False,
                ):
        '''constructor for base zabbix modules'''
        self.zbx = ZabbixAPI(ZabbixConnection(zbx_server, zbx_user, zbx_password, zbx_sslverify, zbx_debug))
        self.zbx_class_name = zbx_class_name
        self.zid = zbx_class_id

    def _list(self, search):
        '''list object'''
        return self.zbx.get_content(self.zbx_class_name, 'get', search)

    def _delete(self, obj_ids):
        '''delete object'''
        return self.zbx.get_content(self.zbx_class_name, 'delete', obj_ids)

    def _create(self, params):
        '''create object'''
        return self.zbx.get_content(self.zbx_class_name, 'create', params)

    def _update(self, params):
        '''update object'''
        return self.zbx.get_content(self.zbx_class_name, 'update', params)

    @staticmethod
    def exists(content, key='result'):
        ''' Check if key exists in content or the size of content[key] > 0 '''
        if not content.has_key(key):
            return False

        if not content[key]:
            return False

        return True

    @staticmethod
    def clean_params(params):
        ''' Check if any key is set to None and remove it'''
        _ = [params.pop(key, None) for key in params.keys() if params[key] is None]

        return params


class Hostgroup(object):
    ''' hostgroup methods'''
    @staticmethod
    def get_host_group_id_by_name(zapi, hg_name):
        '''Get hostgroup id by name'''
        content = zapi.get_content('hostgroup',
                                   'get',
                                   {'filter': {'name': hg_name}})

        return content['result'][0]['groupid']

    @staticmethod
    def get_host_ids_by_group_name(zapi, hg_name):
        '''Get hostgroup id by name'''
        content = zapi.get_content('hostgroup',
                                   'get',
                                   {'filter': {'name': hg_name}})

        results = [host['hostid'] for host in content['result']]
        return results

    @staticmethod
    def get_hostgroup_id(zapi, hg_name):
        '''get a hostgroup id from hg name'''
        content = zapi.get_content('hostgroup',
                                   'get',
                                   {'search': {'name': hg_name}})

        return content['result'][0]['groupid']

class Host(object):
    ''' hostgroup methods'''
    @staticmethod
    def get_host_id_by_name(zapi, host_name):
        '''Get host id by name'''
        content = zapi.get_content('host',
                                   'get',
                                   {'filter': {'name': host_name}})
        return content['result'][0]['hostid']

    @staticmethod
    def get_host_ids_by_hostgroup_name(zapi, host_group):
        '''Get host id by name'''

        hig = Hostgroup.get_host_group_id_by_name(zapi, host_group)

        content = zapi.get_content('host',
                                   'get',
                                   {'groupids': [hig],
                                    'search': {'name': host_group}})
        hostids = []
        for host in content['result']:
            hostids.append(host['hostid'])

        return hostids

class ZbxMaintenance(Zbx):
    '''zabbix module for maintenance'''
    zbx_type = 'maintenance'
    zbx_id = 'maintenanceid'

    def __init__(self,
                 zbx_server,
                 zbx_user,
                 zbx_password,
                 zbx_debug,
                 zbx_sslverify,
                 params):
        '''constructor for zbx module'''
        super(ZbxMaintenance, self).__init__(zbx_server,
                                             zbx_user,
                                             zbx_password,
                                             self.zbx_type,
                                             self.zbx_id,
                                             zbx_debug,
                                             zbx_sslverify)

        self.name = params.get('name', None)
        self.description = params.get('description', None)
        self.start_date = params.get('start_date', None)
        self.duration = params.get('duration', None)
        self.data_collection = params.get('data_collection', None)
        self.hosts = params.get('hosts', None)
        self.hostgroups = params.get('hostgroups', None)

    def list(self, query=None):
        ''' list '''
        if query:
            query = query
        elif self.name == None:
            query = {'search': {'name': ''}}
        else:
            query = {'search': {'name': self.name}}

        query['output'] = 'extend'
        query['selectGroups'] = 'groupids'
        query['selectHosts'] = 'hostids'
        query['selectTimeperiods'] = 'extend'

        rval = self._list(query)

        return rval

    def params(self):
        '''return a dictionary that zabbix expects of the params passed'''
        duration = ZbxMaintenance.get_active_till(self.duration)
        period = self.start_date + duration
        params = {'groupids': None,
                  'hostids': None,
                  'name': self.name,
                  'description': self.description,
                  'active_since': self.start_date,
                  'active_till': period,
                  'timeperiods': [{'start_date': self.start_date, 'period': duration}],
                  'maintenance_type': ZbxMaintenance.get_maintenance_type(self.data_collection)
                 }
        if self.hostgroups:
            params['groupids'] = [Hostgroup.get_host_group_id_by_name(self.zbx, hostgroup) \
                                  for hostgroup in self.hostgroups]
        if self.hosts:
            params['hostids'] = [Host.get_host_id_by_name(self.zbx, host) for host in self.hosts]

        return ZbxMaintenance.clean_params(params)

    def delete(self, mids):
        ''' delete '''
        return self._delete(mids)

    def create(self):
        ''' create '''
        return self._create(self.params())

    def update(self, differences):
        ''' update '''
        return self._update(differences)

    @staticmethod
    def convert_epoch(inval):
        '''convert epoch to datetime'''
        return datetime.datetime.fromtimestamp(int(inval)).strftime('%c')

    @staticmethod
    def get_maintenance_type(invar):
        '''determine maintenance type'''
        if not invar:
            return 1
        return 0

    @staticmethod
    def get_active_till(duration):
        ''' hours to seconds '''
        return duration * 60

    @staticmethod
    def compare_epochs_no_seconds(inv1, inv2):
        '''zabbix times don't include seconds'''
        dt1 = datetime.datetime.fromtimestamp(int(inv1))
        dt2 = datetime.datetime.fromtimestamp(int(inv2))
        if dt1.year == dt2.year and dt1.day == dt2.day and dt1.hour == dt2.hour and dt1.minute == dt2.minute:
            return True

        return False

    # pylint: disable=too-many-branches,too-many-statements,too-many-return-statements
    @staticmethod
    def run_ansible(params):
        '''perform the logic and return results'''
        rval = {'state': params['state']}
        zbx = ZbxMaintenance(params['zbx_server'],
                             params['zbx_user'],
                             params['zbx_password'],
                             params['zbx_debug'],
                             params['zbx_sslverify'],
                             params)

        content = zbx.list()

        if params['state'] == 'list':
            ########
            # List
            ########
            rval['changed'] = False
            for maintenance in content['result']:
                # be nice to user and return intelligible time stamps
                maintenance['active_till'] = ZbxMaintenance.convert_epoch(maintenance['active_till'])
                maintenance['active_since'] = ZbxMaintenance.convert_epoch(maintenance['active_since'])
            rval['results'] = content['result']
            return rval

        elif params['state'] == 'absent':
            ########
            # Absent
            ########
            if not ZbxMaintenance.exists(content):
                rval['changed'] = False
                rval['results'] = []
            else:
                content = zbx.delete([content['result'][0][ZbxMaintenance.zbx_id]])
                rval['changed'] = True
                rval['results'] = content['result']

            return rval

        elif params['state'] == 'present':
            ########
            # Create
            ########
            if not ZbxMaintenance.exists(content):
                content = zbx.create()
                rval['changed'] = True
                if content.has_key('error'):
                    rval['failed'] = True
                    rval['error'] = content['error']
                else:
                    rval['results'] = content['result']

                return rval

            ########
            # Update
            ########
            differences = {}
            zab_results = content['result'][0]
            params = zbx.params()
            for key, value in params.items():
                if key == 'groupids':
                    if zab_results.has_key('groups'):
                        zab_group_ids = [group['groupid'] for group in zab_results['groups']]
                        if set(zab_group_ids) != set(value):
                            differences[key] = value
                    else:
                        differences[key] = value

                elif key == 'hostids':
                    if zab_results.has_key('hosts'):
                        zab_host_ids = [host['hostid'] for host in zab_results['hosts']]
                        if set(zab_host_ids) != set(value):
                            differences[key] = value
                    else:
                        differences[key] = value

                elif key == 'timeperiods':
                    # timeperiods is an array of times; We are going to only check the first timeperiod
                    for t_key, t_value in value[0].items():
                        # zabbix does not allow seconds in maintenance.  It rounds to minutes.
                        # compare start_date correctly
                        if t_key == 'start_date':
                            if not ZbxMaintenance.compare_epochs_no_seconds(zab_results[key][0][t_key], t_value):
                                differences[key] = value
                                break

                        elif str(zab_results[key][0][t_key]) != str(t_value):
                            differences[key] = value
                            break

                elif key in ['active_since', 'active_till']:
                    if not ZbxMaintenance.compare_epochs_no_seconds(zab_results[key], value):
                        differences[key] = value

                elif zab_results[key] != value and zab_results[key] != str(value):
                    differences[key] = value

            if not differences:
                rval['changed'] = False
                for maintenance in content['result']:
                    # be nice to user and return intelligible time stamps
                    maintenance['active_till'] = ZbxMaintenance.convert_epoch(maintenance['active_till'])
                    maintenance['active_since'] = ZbxMaintenance.convert_epoch(maintenance['active_since'])
                rval['results'] = content['result']
                return rval

            # We have differences and need to update
            differences[ZbxMaintenance.zbx_id] = zab_results[ZbxMaintenance.zbx_id]
            differences['hostids'] = params.get('hostids', [])
            differences['groupids'] = params.get('groupids', [])
            differences['active_since'] = params.get('active_since', [])
            differences['active_till'] = params.get('active_till', [])

            content = zbx.update(differences)
            if content.has_key('error'):
                return content

            rval['changed'] = True
            rval['results'] = content['result']
            return rval

        rval['failed'] = True
        rval['error'] = 'State UNKNWON'
        return rval

def main():
    ''' Create a maintenace in zabbix '''

    module = AnsibleModule(
        argument_spec=dict(
            zbx_server=dict(default='https://localhost/zabbix/api_jsonrpc.php', type='str'),
            zbx_user=dict(default=os.environ.get('ZABBIX_USER', None), type='str'),
            zbx_password=dict(default=os.environ.get('ZABBIX_PASSWORD', None), type='str'),
            zbx_debug=dict(default=False, type='bool'),
            zbx_sslverify=dict(default=False, type='bool'),

            state=dict(default='present', choices=['present', 'absent', 'list'], type='str'),
            hosts=dict(default=None, type='list'),
            hostgroups=dict(default=None, type='list'),
            name=dict(default=None, type='str'),
            description=dict(default=None, type='str'),
            start_time=dict(default=int(time.time()), type='int'),
            duration=dict(default=60, type='int'),
            data_collection=dict(default=True, type='bool'),
        ),
        supports_check_mode=False
    )

    rval = ZbxMaintenance.run_ansible(module.params)
    module.exit_json(**rval)

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
if __name__ == '__main__':
    from ansible.module_utils.basic import *
    main()
