# pylint: skip-file

def main():
    '''
    ansible git module for merging
    '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='list', type='str', choices=['list']),
            path=dict(default=None, required=True, type='str'),
            branch=dict(default=None, required=True, type='str'),
            diff_branch=dict(default=None, required=True, type='str'),
            fail_on_diff=dict(default=False, required=False, type='bool'),
        ),
        supports_check_mode=False,
    )
    git = GitDiff(module.params['path'],
                  module.params['branch'],
                  module.params['diff_branch'],
                 )

    state = module.params['state']
    fail_on_diff = module.params['fail_on_diff']

    if state == 'list':
        results = git.diff()

        if fail_on_diff:
            if results['results']:
                module.exit_json(failed=True, changed=False, results=results, state="list")

        module.exit_json(changed=False, results=results, state="list")

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
