# pylint: skip-file

def main():
    '''
    ansible git module for committting
    '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str', choices=['present']),
            msg=dict(default=None, required=True, type='str'),
            path=dict(default=None, required=True, type='str'),
            author=dict(default=None, required=False, type='str'),
            commit_files=dict(default=None, required=False, type='list'),
        ),
        supports_check_mode=False,
    )
    git = GitCommit(module.params['msg'],
                    module.params['path'],
                    module.params['commit_files'],
                    module.params['author'],
                   )

    state = module.params['state']

    if state == 'present':
        results = git.commit()

        if results['returncode'] != 0:
            module.fail_json(msg=results)

        if results.has_key('no_commits'):
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
