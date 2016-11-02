# pylint: skip-file

def main():
    '''
    ansible oc module for route
    '''

    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(default=os.environ.get('STATUSPAGE_API_KEY', ''), type='str'),
            page_id=dict(default=None, type='str', required=True, ),
            org_id=dict(default=None, type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            name=dict(default=None, type='str'),
            unresolved_only=dict(default=False, type='bool'),
            scheduled_only=dict(default=False, type='bool'),
            incident_type=dict(default='realtime', choices=['scheduled', 'realtime', 'historical'], type='str'),
            status=dict(default='investigating',
                        choices=['investigating', 'identified', 'monitoring', 'resolved',
                                 'scheduled', 'in_progress', 'verifying', 'completed'],
                        type='str'),
            update_twitter=dict(default=False, type='bool'),
            msg=dict(default=None, type='str'),
            impact_override=dict(default=None, choices=['none', 'minor', 'major', 'critical'], type='str'),
            components=dict(default=None, type='list'),
            scheduled_for=dict(default=None, type='str'),
            scheduled_until=dict(default=None, type='str'),
            scheduled_remind_prior=dict(default=False, type='bool'),
            scheduled_auto_in_progress=dict(default=False, type='bool'),
            scheduled_auto_completed=dict(default=False, type='bool'),
            verbose=dict(default=False, type='bool'),
        ),
        supports_check_mode=True,
        required_if=[['incident_type', 'scheduled', ['scheduled_for', 'scheduled_until']]],
    )

    if module.params['incident_type'] == 'scheduled':
        if not module.params['status'] in ['scheduled', 'in_progress', 'verifying', 'completed']:
            module.exit_json(msg='If incident type is scheduled, then status must be one of ' +
                             'scheduled|in_progress|verifying|completed')

    elif module.params['incident_type'] in 'realtime':
        if not module.params['status'] in ['investigating', 'identified', 'monitoring', 'resolved']:
            module.exit_json(msg='If incident type is realtime, then status must be one of' +
                             ' investigating|identified|monitoring|resolved')


    results = StatusPageIncident.run_ansible(module.params)
    module.exit_json(**results)

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
if __name__ == '__main__':
    from ansible.module_utils.basic import *
    main()
