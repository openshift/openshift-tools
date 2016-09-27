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
            debug=dict(default=False, type='bool'),
        ),
    )
    ocver = OpenShiftCLI(None, module.params['kubeconfig'], module.params['debug'])

    #pylint: disable=protected-access
    result = ocver._get_version()

    if result['returncode'] != 0:
        module.fail_json(msg=result)

    module.exit_json(changed=False, result=result)


if __name__ == '__main__':
# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
    from ansible.module_utils.basic import *
    main()
