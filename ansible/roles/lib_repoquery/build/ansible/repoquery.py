# pylint: skip-file

def main():
    '''
    ansible repoquery module
    '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='list', type='str', choices=['list']),
            name=dict(default=None, required=True, type='str'),
            query_type=dict(default='repos', required=False, type='str',
                            choices=['installed', 'available', 'recent',
                                     'updates', 'extras', 'all', 'repos']
                           ),
            verbose=dict(default=False, required=False, type='bool'),
            show_duplicates=dict(default=None, required=False, type='bool'),
            match_version=dict(default=None, required=False, type='str'),
        ),
        supports_check_mode=False,
        required_if=[('show_duplicates', True, ['name'])],
    )

    repoquery = Repoquery(module.params['name'],
                          module.params['query_type'],
                          module.params['show_duplicates'],
                          module.params['match_version'],
                          module.params['verbose'],
                         )

    state = module.params['state']

    if state == 'list':
        results = repoquery.repoquery()

        if results['returncode'] != 0:
            module.fail_json(msg=results)

        module.exit_json(changed=False, results=results, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
#if __name__ == '__main__':
#    main()
if __name__ == "__main__":
    from ansible.module_utils.basic import *

    main()
