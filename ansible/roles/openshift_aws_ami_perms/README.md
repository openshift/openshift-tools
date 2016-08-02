openshift_aws_ami_perms
=========

Ansible role for adding ami perms

Requirements
------------

Ansible Modules:


Role Variables
--------------

osaap_src_ami_access_id: AWS Access Key (with permissions to share) of the SRC account
osaap_src_ami_access_key  AWS Secret Key (with permissions to share) of the SRC account
osaap_dest_aws_accountid: The account that needs access to the AMI (launch and copy)
osaap_region: region the ami lives in and will be shared in
osaap_image_id: AMI id

Dependencies
------------


Example Playbook
----------------

  - role: tools_roles/openshift_aws_ami_perms
    osaap_src_ami_access_id: XXXXXXXXXX
    osaap_src_ami_access_key: YYYYYYYYY
    osaap_dest_aws_accountid: 123456789
    osaap_region: us-west-1
    osaap_image_id: ami-123456


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
