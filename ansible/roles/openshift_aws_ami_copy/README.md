openshift_aws_ami_perms
=========

Ansible role for copying an AMI

Requirements
------------

Ansible Modules:


Role Variables
--------------

osaac_aws_access_key: AWS Access Key (can chose to not pass in and just read env vars)
osaac_aws_secret_key: AWS Secret Key (can chose to not pass in and just read env vars)
osaac_src_ami: source AMI id to copy from
osaac_region: region where the AMI is found
osaac_name: name to assign to new AMI
osaac_kms_alias: AWS IAM KMS alias name of the key to use for encryption
osaac_ami_directory: directory for where the role should place the yaml file that records the id of the AMI that was generated

Dependencies
------------


Example Playbook
----------------

  - role: tools_roles/openshift_aws_ami_copy
    osaac_aws_access_key: XXXXXXXXXX
    osaac_aws_secret_key: YYYYYYYYY
    osaac_region: us-west-1
    osaac_src_ami: ami-123456
    osaac_name: "new AMI with encryption"
    osaac_encrypt: True
    osaac_kms_alias: "alias/custom_kms_key"
    osaac_ami_directory: "/var/lib/git/repo/ami"


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
