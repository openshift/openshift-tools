# pylint: skip-file

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
