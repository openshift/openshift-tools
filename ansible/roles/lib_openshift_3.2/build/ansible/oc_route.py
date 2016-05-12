# pylint: skip-file

def get_cert_data(path, content):
    '''get the data for a particular value'''
    if not path and not content:
        return None

    rval = None
    if path and os.path.exists(path) and os.access(path, os.R_OK):
        rval = open(path).read()
    elif content:
        rval = content

    return rval

#pylint: disable=too-many-branches
def main():
    '''
    ansible oc module for route
    '''

    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            debug=dict(default=False, type='bool'),
            name=dict(default=None, required=True, type='str'),
            namespace=dict(default=None, required=True, type='str'),
            tls_termination=dict(default=None, type='str'),
            dest_cacert_path=dict(default=None, type='str'),
            cacert_path=dict(default=None, type='str'),
            cert_path=dict(default=None, type='str'),
            key_path=dict(default=None, type='str'),
            dest_cacert_content=dict(default=None, type='str'),
            cacert_content=dict(default=None, type='str'),
            cert_content=dict(default=None, type='str'),
            key_content=dict(default=None, type='str'),
            service_name=dict(default=None, type='str'),
            host=dict(default=None, type='str'),
        ),
        mutually_exclusive=[('dest_cacert_path', 'dest_cacert_content'),
                            ('cacert_path', 'cacert_content'),
                            ('cert_path', 'cert_content'),
                            ('key_path', 'key_content'),
                           ],
        supports_check_mode=True,
    )
    files = {'destcacert': {'path': module.params['dest_cacert_path'],
                            'content': module.params['dest_cacert_content'],
                            'value': None,
                           },
             'cacert':  {'path': module.params['cacert_path'],
                         'content': module.params['cacert_content'],
                         'value': None,
                        },
             'cert':  {'path': module.params['cert_path'],
                       'content': module.params['cert_content'],
                       'value': None,
                      },
             'key':  {'path': module.params['key_path'],
                      'content': module.params['key_content'],
                      'value': None,
                     },
            }
    if module.params['tls_termination']:
        for key, option in files.items():
            if key == 'destcacert' and module.params['tls_termination'] != 'reencrypt':
                continue

            option['value'] = get_cert_data(option['path'], option['content'])

            if not option['value']:
                module.fail_json(msg='Verify that you pass a value for %s' % key)

    rconfig = RouteConfig(module.params['name'],
                          module.params['namespace'],
                          module.params['kubeconfig'],
                          files['destcacert']['value'],
                          files['cacert']['value'],
                          files['cert']['value'],
                          files['key']['value'],
                          module.params['host'],
                          module.params['tls_termination'],
                          module.params['service_name'],
                         )
    oc_route = OCRoute(rconfig,
                       verbose=module.params['debug'])

    state = module.params['state']

    api_rval = oc_route.get()

    #####
    # Get
    #####
    if state == 'list':
        module.exit_json(changed=False, results=api_rval['results'], state="list")

    ########
    # Delete
    ########
    if state == 'absent':
        if oc_route.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a delete.')

            api_rval = oc_route.delete()

            module.exit_json(changed=True, results=api_rval, state="absent")
        module.exit_json(changed=False, state="absent")

    if state == 'present':
        ########
        # Create
        ########
        if not oc_route.exists():

            if module.check_mode:
                module.exit_json(changed=False, msg='Would have performed a create.')

            # Create it here
            api_rval = oc_route.create()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_route.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Update
        ########
        if oc_route.needs_update():
            api_rval = oc_route.update()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            # return the created object
            api_rval = oc_route.get()

            if api_rval['returncode'] != 0:
                module.fail_json(msg=api_rval)

            module.exit_json(changed=True, results=api_rval, state="present")

        module.exit_json(changed=False, results=api_rval, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *

main()
