# pylint: skip-file

# pylint: disable=too-many-branches
def main():
    '''
    ansible oc module for image import
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'list']),
            debug=dict(default=False, type='bool'),
            namespace=dict(default='default', type='str'),
            registry_url=dict(default=None, type='str'),
            image_name=dict(default=None, type='str'),
            image_tag=dict(default=None, type='str'),
            content_type=dict(default='raw', choices=['yaml', 'json', 'raw'], type='str'),
            force=dict(default=False, type='bool'),
        ),

        supports_check_mode=True,
    )
    ocimage = OCImage(module.params['namespace'],
                      module.params['registry_url'],
                      module.params['image_name'],
                      module.params['image_tag'],
                      kubeconfig=module.params['kubeconfig'],
                      verbose=module.params['debug'])

    state = module.params['state']

    api_rval = ocimage.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval, state="list")

    if not module.params['image_name']:
        module.fail_json(msg='Please specify a name when state is absent|present.')

    if state == 'present':

        ########
        # Create
        ########
        if not Utils.exists(api_rval['results'], module.params['image_name']):

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            api_rval = ocimage.create(module.params['registry_url'],
                                      module.params['image_name'],
                                      module.params['image_tag'])

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        # image exists, no change
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
