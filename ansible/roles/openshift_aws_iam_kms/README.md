openshift_aws_iam_kms
=========

Ansible role to create Openshift AWS IAM KMS keys for Openshift Operations.

Requirements
------------

Ansible Modules:

oo_iam_kms

Role Variables
--------------

  osaik_region: AWS region to create KMS key
  osaik_alias: Alias name to assign to created KMS key

Dependencies
------------

lib_utils

Example Playbook
----------------

- role: ops_roles/openshift_aws_iam_kms
  osaik_region: 'us-east-1'
  osaik_alias: 'alias/clusterABC_kms'


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
