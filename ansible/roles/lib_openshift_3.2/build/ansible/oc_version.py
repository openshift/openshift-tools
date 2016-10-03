# pylint: skip-file

# pylint: disable=too-many-branches
def main():
    '''
    ansible oc module for version
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            version=dict(default=True, type='bool'),
            state=dict(default='list', type='str',
                       choices=['list']),
            debug=dict(default=False, type='bool'),
        ),
    )
    oc_version = OCVersion(module.params['kubeconfig'],
                           module.params['debug'])

    state = module.params['state']

    if state == 'list':

        #pylint: disable=protected-access
        result = oc_version.get()

        module.exit_json(changed=False, result=result)

if __name__ == '__main__':
# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
    from ansible.module_utils.basic import *
    main()
