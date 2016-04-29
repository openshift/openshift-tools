# pylint: skip-file

def main():
    '''
    ansible oadm module for ca
    '''

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str',
                       choices=['present']),
            debug=dict(default=False, type='bool'),
            kubeconfig=dict(default='/etc/origin/master/admin.kubeconfig', type='str'),
            cmd=dict(default=None, require=True, type='str'),

            # oadm ca create-master-certs [options]
            cert_dir=dict(default=None, type='str'),
            hostnames=dict(default=[], type='list'),
            master=dict(default=None, type='str'),
            public_master=dict(default=None, type='str'),
            overwrite=dict(default=False, type='bool'),
            signer_name=dict(default=None, type='str'),

            # oadm ca create-key-pair [options]
            private_key=dict(default=None, type='str'),
            public_key=dict(default=None, type='str'),

            # oadm ca create-server-cert [options]
            cert=dict(default=None, type='str'),
            key=dict(default=None, type='str'),
            signer_cert=dict(default=None, type='str'),
            signer_key=dict(default=None, type='str'),
            signer_serial=dict(default=None, type='str'),

            # name
            # oadm ca create-signer-cert [options]

        ),
        supports_check_mode=True,
    )

    # pylint: disable=line-too-long
    config = CertificateAuthorityConfig(module.params['cmd'],
                                        module.params['kubeconfig'],
                                        module.params['debug'],
                                        {'cert_dir':      {'value': module.params['cert_dir'], 'include': True},
                                         'cert':          {'value': module.params['cert'], 'include': True},
                                         'hostnames':     {'value': ','.join(module.params['hostnames']), 'include': True},
                                         'master':        {'value': module.params['master'], 'include': True},
                                         'public_master': {'value': module.params['public_master'], 'include': True},
                                         'overwrite':     {'value': module.params['overwrite'], 'include': True},
                                         'signer_name':   {'value': module.params['signer_name'], 'include': True},
                                         'private_key':   {'value': module.params['private_key'], 'include': True},
                                         'public_key':    {'value': module.params['public_key'], 'include': True},
                                         'key':           {'value': module.params['key'], 'include': True},
                                         'signer_cert':   {'value': module.params['signer_cert'], 'include': True},
                                         'signer_key':    {'value': module.params['signer_key'], 'include': True},
                                         'signer_serial': {'value': module.params['signer_serial'], 'include': True},
                                        })


    oadm_ca = CertificateAuthority(config)

    state = module.params['state']

    if state == 'present':
        ########
        # Create
        ########
        if not oadm_ca.exists() or module.params['overwrite']:

            if module.check_mode:
                module.exit_json(changed=False, msg="Would have created the certificate.", state="present")

            api_rval = oadm_ca.create()

            module.exit_json(changed=True, results=api_rval, state="present")

        ########
        # Exists
        ########
        api_rval = oadm_ca.get()
        module.exit_json(changed=False, results=api_rval, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
from ansible.module_utils.basic import *
main()
