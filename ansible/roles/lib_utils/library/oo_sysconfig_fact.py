#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4

''' sysconfig_fact module

    The purpose of this module is to read the contents of an /etc/sysconfig file
    and set Ansible facts for each value.
'''


from StringIO import StringIO
import ConfigParser

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

    strbuffer = StringIO()
    strbuffer.write("[main]\n")

    with open(param_src, 'r') as src_file:
        strbuffer.write(src_file.read())

    strbuffer.seek(0)
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.readfp(strbuffer)

    facts = {}
    facts[param_name] = {}
    for item in config.items("main"):
        facts[param_name][item[0]] = item[1]

    module.exit_json(changed=False, ansible_facts=facts)

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
