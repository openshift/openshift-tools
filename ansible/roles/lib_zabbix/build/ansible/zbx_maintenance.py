# pylint: skip-file

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
            start_date=dict(default=int(time.time()), type='int'),
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
