#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4

''' cat_fact module

    The purpose of this module is to cat the contents of a file into an Ansible fact for use later.
'''

def main():
    ''' Main function of this module.
    '''
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            name=dict(required=True, type='str'),
        ),
        supports_check_mode=False
    )

    param_src = module.params.get('src')
    param_name = module.params.get('name')

    facts = {}

    with open(param_src, 'r') as src_file:
        facts[param_name] = src_file.read()


    module.exit_json(changed=False, ansible_facts=facts)

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
