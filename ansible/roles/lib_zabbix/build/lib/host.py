# pylint: skip-file

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
