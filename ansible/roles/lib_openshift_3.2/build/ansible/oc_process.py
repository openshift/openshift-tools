# pylint: skip-file

# pylint: disable=too-many-branches
def main():
    '''
    ansible oc module for services
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str', choices=['present', 'list']),
            debug=dict(default=False, type='bool'),
            namespace=dict(default='default', type='str'),
            template_name=dict(default=None, type='str'),
            content=dict(default=None, type='str'),
            params=dict(default=None, type='dict'),
            create=dict(default=False, type='bool'),
            reconcile=dict(default=True, type='bool'),
        ),
        supports_check_mode=True,
    )
    ocprocess = OCProcess(module.params['namespace'],
                          module.params['template_name'],
                          module.params['params'],
                          module.params['create'],
                          kubeconfig=module.params['kubeconfig'],
                          tdata=module.params['content'],
                          verbose=module.params['debug'])

    state = module.params['state']

    api_rval = ocprocess.get()

    if state == 'list':
        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval)

        module.exit_json(changed=False, results=api_rval, state="list")

    elif state == 'present':
        if not ocprocess.exists() or not module.params['reconcile']:
            #FIXME: this code will never get run in a way that succeeds when
            #       module.params['reconcile'] is true. Because oc_process doesn't
            #       create the actual template, the check of ocprocess.exists()
            #       is meaningless. Either it's already here and this code
            #       won't be run, or this code will fail because there is no
            #       template available for oc process to use. Have we conflated
            #       the template's existence with the existence of the objects
            #       it describes?


            # Create it here
            api_rval = ocprocess.process()
            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        # verify results
        update = False
        rval = []
        all_results = ocprocess.needs_update()
        for obj, status in all_results:
            if status:
                ocprocess.delete(obj)
                results = ocprocess.create_obj(obj)
                results['kind'] = obj['kind']
                rval.append(results)
                update = True

        if not update:
            module.exit_json(changed=update, results=api_rval, state="present")

        for cmd in rval:
            if cmd['returncode'] != 0:
                module.fail_json(changed=update, results=rval, state="present")

        module.exit_json(changed=update, results=rval, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
if __name__ == '__main__':
    from ansible.module_utils.basic import *
    main()
