# pylint: skip-file

def main():
    '''
    ansible git module for pushing
    '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str', choices=['present']),
            path=dict(default=None, required=True, type='str'),
            remote=dict(default=None, required=True, type='str'),
            src_branch=dict(default=None, required=True, type='str'),
            dest_branch=dict(default=None, required=True, type='str'),
            ssh_key=dict(default=None, required=False, type='str'),
        ),
        supports_check_mode=False,
    )
    git = GitPush(module.params['path'],
                  module.params['remote'],
                  module.params['src_branch'],
                  module.params['dest_branch'],
                  module.params['ssh_key'])

    state = module.params['state']

    if state == 'present':
        results = git.push()

        if results['returncode'] != 0:
            module.fail_json(msg=results)

        if results.has_key('no_push_needed'):
            module.exit_json(changed=False, results=results, state="present")

        module.exit_json(changed=True, results=results, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
if __name__ == '__main__':
    from ansible.module_utils.basic import *
    main()
