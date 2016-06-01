openshift_aws_ami_perms
=========

Ansible role for adding ami perms

Requirements
------------

Ansible Modules:


Role Variables
--------------

osaak_users: list of dicts of users
osaak_region: ec2_region to install the keys

Dependencies
------------


Example Playbook
----------------

sample-osaak_users:
- user1:
    username: user1
    pub_key: <user1 ssh public key>
- user2:
    username: user2
    pub_key: <user2 ssh public key>

sample_osaak_region: us-east-1

- role: tools_roles/openshift_aws_add_keys
  osaak_users: "{{ sample-osaak_users }}"
  osaak_region: "{{ sample_osaak_region }}"



License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
