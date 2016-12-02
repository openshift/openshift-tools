openshift_sso_app
=========

Ansible role for setting up and configuring a Single Sign-on OpenShift Application

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2


Role Variables
--------------

- `osso_namespace`: The project namespace that the application should be deployed to
- `osso_app_domain`: The DNS name of the SSO application (e.g. login.example.com)
- `osso_authdata_yml_content`: The contents of the `authdata.yml` file to be added to the secret. See https://github.com/openshift/openshift-tools/blob/prod/web/simplesaml_mods/authorizeyaml/docs/authorize.txt for information on how to format this file.
- `osso_authorized_keys_content`: The contents of the `authorized_keys` file. Each key should have a prefix command option like `command="get_saml_token jsmith@example.com"`
- `osso_configdata_yml_content`: The contents of the `configdata.yml` file. See https://github.com/openshift/openshift-tools/blob/stg/docker/oso-saml-sso/example/configdata.yml for an example of this data.
- `osso_site_cert_content`: The front-end certificate for the SSO application. The certificate should be valid for the DNS name specified in `osso_app_domain`.
- `osso_site_key_content`: The private key corresponding to the certificate specified in `osso_site_cert_content`.
- `osso_site_ca_cert_content`: The certificate of the certificate authority (CA) that signed the certificate specified in `osso_site_cert_content`.
- `osso_dest_ca_cert_content`: The CA certificate that the router will use when connecting to the pod for purposes of verification. Should be a self-signed root certificate as OpenShift/HAProxy will not properly validate any other certificate in the trust chain.
- `osso_monitoring_ssh_private_key`: The private SSH key that can be used to obtain SAML tokens for purposes of monitoring
- `osso_monitoring_ssh_public_key`: The public SSH key corresponding to `osso_monitoring_ssh_private_key`. Should be installed in `osso_authorized_keys_content`.
- `osso_aws_accounts_txt_content`: A file with one entry per line. Each line represents a single AWS account and should be in the format `account_name:123456789012`
- `osso_zagg_config`: A dictionary with config data for the ZAGG monitoring client, to populate `zagg_client.yaml`. Expected values: `url`, `user`, `password`, `ssl_verify`, `verbose` and `debug`

Dependencies
------------


Example Playbook
----------------


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
