verify_aws_accountid
=========
This role checks to see if the AWS Key matches an account ID. If they don't match, it will fail

Configure
------------

None

Role Variables
--------------

vawsid_accountid: The account ID to check against

Dependencies
------------

None

Example Playbook
----------------

  - role: tools_roles/verify_aws_accountid
    vawsid_accountid: "{{ g_aws_account_id }}"

License
-------

ASL 2.0

Author Information
------------------

OpenShift operations, Red Hat, Inc
