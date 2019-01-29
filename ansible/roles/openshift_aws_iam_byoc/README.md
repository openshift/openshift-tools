openshift_aws_iam_byoc
=========

Ansible role for creating IAM resources for Bring Your Own Cloud (BYOC) in AWS.

Requirements
------------

Ansible Modules:


Role Variables
--------------

osaib_state: one of: present, absent
osaib_account_id: AWS Account ID for target of trush policy for the role.

Dependencies
------------


Example Playbook
----------------


    - role: tools_roles/openshift_aws_role
        osaib_state: present
        osaib_account_id: 1234567


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
