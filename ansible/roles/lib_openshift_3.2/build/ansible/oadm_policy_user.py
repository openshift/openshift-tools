# pylint: skip-file
#Manage policy
#
#Usage:
#  oadm policy [options]
#
#Available Commands:
#  add-role-to-user                Add users to a role in the current project
#  remove-role-from-user           Remove user from role in the current project
#  remove-user                     Remove user from the current project
#  add-cluster-role-to-user        Add users to a role for all projects in the cluster
#  remove-cluster-role-from-user   Remove user from role for all projects in the cluster
#  add-scc-to-user                 Add users to a security context constraint
#  remove-scc-from-user            Remove user from scc
#
#Use "oadm help <command>" for more information about a given command.
#Use "oadm options" for a list of global command-line options (applies to all commands).
#

def main():
    '''
    ansible oadm module for user policy
    '''

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str',
                       choices=['present', 'absent']),
            debug=dict(default=False, type='bool'),
            resource_name=dict(required=True, type='str'),
            namespace=dict(default=None, type='str'),
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),

            # add-role-to-user
            user=dict(required=True, type='str'),
            resource_kind=dict(required=True, choices=['role', 'cluster-role', 'scc'], type='str'),
        ),
        supports_check_mode=True,
    )
    state = module.params['state']

    action = None
    if state == 'present':
        action = 'add-' + module.params['resource_kind'] + '-to-user'
    else:
        action = 'remove-' + module.params['resource_kind'] + '-from-user'

    uconfig = OadmPolicyUserConfig(module.params['namespace'],
                                   module.params['kubeconfig'],
                                   {'action': {'value': action, 'include': False},
                                    'user': {'value': module.params['user'], 'include': False},
                                    'resource_kind': {'value': module.params['resource_kind'], 'include': False},
                                    'name': {'value': module.params['resource_name'], 'include': False},
                                   })

    oadmpolicyuser = OadmPolicyUser(uconfig)

    ########
    # Delete
    ########
    if state == 'absent':
        if not oadmpolicyuser.exists():
            module.exit_json(changed=False, state="absent")

        if module.check_mode:
            module.exit_json(changed=False, msg='Would have performed a delete.')

        api_rval = oadmpolicyuser.perform()

        if api_rval['returncode'] != 0:
            module.fail_json(msg=api_rval)

        module.exit_json(changed=True, results=api_rval, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        results = oadmpolicyuser.exists()
        if isinstance(results, dict) and results.has_key('returncode') and results['returncode'] != 0:
            module.fail_json(msg=results)

        if not results:

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            api_rval = oadmpolicyuser.perform()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        module.exit_json(changed=False, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *
main()
