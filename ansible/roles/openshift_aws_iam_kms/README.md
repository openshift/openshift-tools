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
  osaik_kms_directory: directory to create (if necessary) to store the KMS alias and ARN details as a file 'kms.yml' in the specified directory

Dependencies
------------

lib_utils

Example Playbook
----------------

- role: ops_roles/openshift_aws_iam_kms
  osaik_region: 'us-east-1'
  osaik_alias: 'alias/clusterABC_kms'
  osaik_kms_directory: '/tmp/store_kms_file_here'


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
