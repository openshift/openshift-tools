openshift_aws_iam_kms
=========

Ansible role to create Openshift AWS IAM KMS keys for Openshift Operations.

Requirements
------------

Ansible Modules:

oo_ec2_elb_migrate

Role Variables
--------------

  osapm_from_az: AZ to evacute PVs from
  oaspm_to_az: target AZ to create new PVs in
  osapm_region: AWS region
  osapm_aws_access_key: AWS key to use (or leave blank to use env vars)
  osapm_aws_secret_key: AWS secret to use (or leave blank to use env vars)

Dependencies
------------

lib_utils

Example Playbook
----------------

# Run against a single OpenShift master node
- include_role:
    name: tools_roles/openshift_aws_pv_move
  vars:
    osapm_region: 'us-east-1'
    osapm_from_az: 'us-east-1a'
    osapm_to_az: 'us-east-1c'
    osapm_aws_access_key: "{{ aws_access_key }}"
    osapm_aws_secret_key: "{{ aws_secret_key }}"


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
