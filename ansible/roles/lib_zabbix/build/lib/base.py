# pylint: skip-file

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

