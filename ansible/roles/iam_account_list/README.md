IAM Account List
=========

Copies the list of IAM accounts.

Requirements
------------

None

Role Variables
--------------

- `ial_iam_account_file`:
    Path to output file.

Set Facts
---------

None

Dependencies
------------

None

Example Playbook
----------------

    - hosts: bastion
      roles:
        - role: tools_roles/iam_account_list
          ial_iam_account_file: /etc/openshift_tools/ops_iam_user_list.yml

License
-------

ASL 2.0

Author Information
------------------

OpenShift operations, Red Hat, Inc
