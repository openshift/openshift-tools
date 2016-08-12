Role Name
=========

A brief description of the role goes here.

Requirements
------------

Ansible 2.0 will be required to use the exclude Docker from the updates

Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------

- hosts: opstest-master-0963a
  gather_facts: no
  user: root
  roles:
  - role: openshift_master_upgrade/ 

License
-------

Apache

Author Information
------------------

Max Whittingham <mwhittingham@redhat.com>
