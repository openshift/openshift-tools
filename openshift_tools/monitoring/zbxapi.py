#!/usr/bin/env python
'''
  ZabbixAPI library

if __name__ == '__main__':
    server = 'http://localhost/zabbix/api_jsonrpc.php'
    username = ''
    password = ''
    zbc = ZabbixConnection(server, username, password)
    zbx = ZabbixAPI(data)
    print zbx.get_content('user', 'get', {})

'''
# vim: expandtab:tabstop=4:shiftwidth=4

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
#  Purpose: An ansible module to communicate with zabbix.
#

# pylint: disable=line-too-long
# Disabling line length for readability

import json
import httplib2
import copy

class ZabbixAPIError(Exception):
    '''
        ZabbixAPIError
        Exists to propagate errors up from the api
    '''
    pass

# Disabling to have DTO
# pylint: disable=too-few-public-methods
class ZabbixConnection(object):
    '''
    Placeholder for connection options
    '''
    def __init__(self, server, username, password, verbose=False):
        self.server = server
        self.username = username
        self.password = password
        self.verbose = verbose

class ZabbixAPI(object):
    '''
        ZabbixAPI class
    '''
    classes = {
        'Action': ['create', 'delete', 'get', 'update'],
        'Alert': ['get'],
        'Application': ['create', 'delete', 'get', 'massadd', 'update'],
        'Configuration': ['export', 'import'],
        'Dhost': ['get'],
        'Dcheck': ['get'],
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
        self.use_ssl = False
        if self.server.startswith('https'):
            self.use_ssl = False
        self.auth = None

        for cname, _ in self.classes.items():
            setattr(self, cname.lower(), getattr(self, cname)(self))

        # pylint: disable=no-member
        # This method does not exist until the metaprogramming executed
        results = self.user.login(user=self.username, password=self.password)

        if results[0]['status'] == '200':
            if results[1].has_key('result'):
                self.auth = results[1]['result']
            elif results[1].has_key('error'):
                raise ZabbixAPIError("Unable to authenticate with zabbix server. {0} ".format(results[1]['error']))
        else:
            raise ZabbixAPIError("Error in call to zabbix. Http status: {0}.".format(results[0]['status']))

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
        http_method = "POST"
        jsonrpc = "2.0"
        rid = 1

        http = None
        if self.use_ssl:
            http = httplib2.Http()
        else:
            http = httplib2.Http(disable_ssl_certificate_validation=True,)

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
            print body
            print method
            print headers
            httplib2.debuglevel = 1

        response, content = http.request(self.server, http_method, body, headers)

        if response['status'] not in ['200', '201']:
            raise ZabbixAPIError('Error calling zabbix.  Zabbix returned %s' % response['status'])

        if self.verbose:
            print response
            print content

        try:
            content = json.loads(content)
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

