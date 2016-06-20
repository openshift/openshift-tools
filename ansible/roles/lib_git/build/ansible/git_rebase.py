# pylint: skip-file

def main():
    '''
    ansible git module for merging
    '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str', choices=['present']),
            path=dict(default=None, required=True, type='str'),
            branch=dict(default=None, required=True, type='str'),
            rebase_branch=dict(default=None, required=True, type='str'),
        ),
        supports_check_mode=False,
    )
    git = GitRebase(module.params['path'],
                  module.params['branch'],
                  module.params['rebase_branch'])

    state = module.params['state']

    if state == 'present':
        results = git.rebase()

        if results['returncode'] != 0:
            module.fail_json(msg=results)

        if results.has_key('no_rebase_needed'):
            module.exit_json(changed=False, results=results, state="present")

        module.exit_json(changed=True, results=results, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
#if __name__ == '__main__':
#    main()
from ansible.module_utils.basic import *

main()
