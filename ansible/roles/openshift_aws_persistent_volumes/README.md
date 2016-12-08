openshift_aws_persistent_volumes
=========

Ansible role to create Openshift AWS PV's for Openshift Operations.

Requirements
------------

Ansible Modules:

ec2_vol20

RPM Packages
python package:
python-boto

Role Variables
--------------

  osapv_volumes: volume dict definition of PV's to create

  example:
  osapv_volumes:
  - size: 5
    count: 2
  - size: 1
    count: 3

  osapv_encrypted: true|false whether to make PVs encrypted
  oapv_kms_alias: IAM KMS alias name (with "alias/" prefix) to use for PV encryption (if blank, it will use the default KMS encryption key)

Dependencies
------------

lib_ansible20

Example Playbook
----------------

- role: ops_roles/openshift_aws_persistent_volumes
  osapv_volumes: "{{ g_pvs }}"
  osapv_encrypt: True
  osapv_kms_alias: "alias/pv_key_kms"


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
