# pylint: skip-file

def main():
    '''
    ansible module for statuspage components
    '''

    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(default=os.environ.get('STATUSPAGE_API_KEY', ''), type='str'),
            page_id=dict(default=None, type='str', required=True, ),
            org_id=dict(default=None, type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            name=dict(default=None, type='str'),
            description=dict(default=None, type='str'),
            group_name=dict(default=None, type='str'),
            status=dict(default='operational', chioces=["operational", "degraded_performance",
                                                        "partial_outage", "major_outage"],
                        type='str'),
            verbose=dict(default=False, type='bool'),
        ),
        supports_check_mode=True,
    )

    results = StatusPageComponent.run_ansible(module.params)
    module.exit_json(**results)

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
if __name__ == '__main__':
    from ansible.module_utils.basic import *
    main()
