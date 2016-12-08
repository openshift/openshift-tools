# pylint: skip-file

def main():
    '''
    ansible oc module for project
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            debug=dict(default=False, type='bool'),
            name=dict(default=None, require=True, type='str'),
            display_name=dict(default=None, type='str'),
            node_selector=dict(default=None, type='str'),
            description=dict(default=None, type='str'),
            admin=dict(default=None, type='str'),
            admin_role=dict(default=None, type='str'),
        ),
        supports_check_mode=True,
    )

    pconfig = ProjectConfig(module.params['name'],
                            module.params['name'],
                            module.params['kubeconfig'],
                            {'admin': {'value': module.params['admin'], 'include': True},
                             'admin_role': {'value': module.params['admin_role'], 'include': True},
                             'description': {'value': module.params['description'], 'include': True},
                             'display_name': {'value': module.params['display_name'], 'include': True},
                             'node_selector': {'value': module.params['node_selector'], 'include': True},
                            })
    oadm_project = OadmProject(pconfig,
                               verbose=module.params['debug'])

    state = module.params['state']

    api_rval = oadm_project.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if oadm_project.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = oadm_project.delete()

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not oadm_project.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = oadm_project.create()

            # return the created object
            api_rval = oadm_project.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        if oadm_project.needs_update():
            api_rval = oadm_project.update()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oadm_project.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        module.exit_json(changed=False, results=api_rval, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
if __name__ == '__main__':
    from ansible.module_utils.basic import *
    main()
