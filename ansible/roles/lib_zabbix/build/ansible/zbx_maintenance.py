# pylint: skip-file

def get_maintenance_type(invar):
    '''determine maintenance type'''
    if not invar:
        return 1
    return 0

def get_active_till(duration)
    ''' hours to seconds '''
    return duration * 60 * 60

def get_host_id_by_name(zapi, host_name):
    '''Get host id by name'''
    content = zapi.get_content('host',
                               'get',
                               {'filter': {'name': host_name}})

    return content['result'][0]['hostid']

def get_host_group_id_by_name(zapi, hg_name):
    '''Get hostgroup id by name'''
    content = zapi.get_content('hostgroup',
                               'get',
                               {'filter': {'name': hg_name}})

    return content['result'][0]['groupid']


def get_hostgroup_id(zapi, hg_name):
    '''get a hostgroup id from hg name'''
    content = zapi.get_content('hostgroup',
                               'get',
                               {'search': {'name': hg_name},
                               })
    return content['result'][0]['groupid']


def main():
    ''' Create a maintenace in zabbix '''

    module = AnsibleModule(
        argument_spec=dict(
            zbx_server=dict(default='https://localhost/zabbix/api_jsonrpc.php', type='str'),
            zbx_user=dict(default=os.environ.get('ZABBIX_USER', None), type='str'),
            zbx_password=dict(default=os.environ.get('ZABBIX_PASSWORD', None), type='str'),
            zbx_debug=dict(default=False, type='bool'),

            host=dict(default=None, type='list'),
            hostgroup=dict(default=None, type='list'),
            name=dict(default=None, type='str'),
            description=dict(default=None, type='str'),
            start_time=dict(default=None, type='int'),
            duration=dict(default=8, type='int'),
            data_collection=dict(default=True, type='bool'),
        ),
        #supports_check_mode=True
    )

    zapi = ZabbixAPI(ZabbixConnection(module.params['zbx_server'],
                                      module.params['zbx_user'],
                                      module.params['zbx_password'],
                                      module.params['zbx_debug']))

    #Set the instance and the template for the rest of the calls
    zbx_class_name = 'maintenance'
    idname = "maintenanceid"
    state = module.params['state']

    content = zapi.get_content(zbx_class_name,
                               'get',
                               {'search': {'name': module.params['name']},
                               })

    # Get
    if state == 'list':
        module.exit_json(changed=False, results=content['result'], state="list")

    # Delete
    if state == 'absent':
        if not exists(content):
            module.exit_json(changed=False, state="absent")
        content = zapi.get_content(zbx_class_name, 'delete', [content['result'][0][idname]])
        module.exit_json(changed=True, results=content['result'], state="absent")

    # Create and Update
    if state == 'present':
        act_since = module.param['start_time']
        act_till = get_active_till(module.param['duration'])
        params = {'hostids': get_host_id_by_name(zapi, module.params['host']),
                  'groupids':  get_hostgroup_id(zapi, module.params['hostgroup']),
                  'description':  module.params['description'],
                  'name':  module.params['name'],
                  'active_since': get_priority(module.params['priority']),
                  'active_till': act_since + act_till,
                  'maintenance_type': get_maintenance_type(module.params['data_collection'])
                  'timeperiods': [{'start_time': act_since, 'period': act_till}],

                 }

        # Remove any None valued params
        _ = [params.pop(key, None) for key in params.keys() if params[key] is None]

        #******#
        # CREATE
        #******#
        if not exists(content):
            # if we didn't find it, create it
            content = zapi.get_content(zbx_class_name, 'create', params)

            if content.has_key('error'):
                module.exit_json(failed=True, changed=True, results=content['error'], state="present")

            module.exit_json(changed=True, results=content['result'], state='present')

        ########
        # UPDATE
        ########
        differences = {}
        zab_results = content['result'][0]
        for key, value in params.items():

            if zab_results[key] != value and zab_results[key] != str(value):
                differences[key] = value

        if not differences:
            module.exit_json(changed=False, results=zab_results, state="present")

        # We have differences and need to update
        differences[idname] = zab_results[idname]
        content = zapi.get_content(zbx_class_name, 'update', differences)
        module.exit_json(changed=True, results=content['result'], state="present")


    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
