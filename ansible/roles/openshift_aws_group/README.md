openshift_aws_group
=========

Ansible role for creating IAM groups in AWS. This role expects a policy as well, and will associate the policy with the AWS Group

Requirements
------------

Ansible Modules:


Role Variables
--------------

osagr_name: Group name to be created
osagr_policy_name: name of the policy that will be associated
osagr_json_policy: IAM policy, in json format


Dependencies
------------


Example Playbook
----------------


  - role: tools_roles/openshift_aws_group
    osagr_name: test_users
    osagr_policy_name: test_user_policy
    osagr_json_policy: "{{ tesr_user_policy_in_json }}"


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
