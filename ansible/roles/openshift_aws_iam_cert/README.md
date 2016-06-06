openshift_aws_group
=========

Ansible role for creating IAM groups in AWS

Requirements
------------

Ansible Modules:


Role Variables
--------------

osaic_iam_certname: Cert name in IAM
osaic_cert: path to cert
osaic_key: path_to_key
osaic_chain_cert: path to chain cert.  Optional
osaic_dest_file: place to write the iam data

Dependencies
------------


Example Playbook
----------------

  - role: tools_roles/openshift_aws_iam_cert
    osaic_iam_certname: cert_name_in_iam
    osaic_cert: /path/to/cert
    osaic_key: /path/to/key
    osaic_chain_cert: /path/to/chain_cert
    osaic_dest_file: /path/to/yaml_file/file.yml

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
