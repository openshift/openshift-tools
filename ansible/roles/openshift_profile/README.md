Role Name
=========

A role designed to expose the openshift_profile=web port in the atomic-openshift-node process for additional debugging
Requirements
------------

None

Role Variables
--------------

op_openshift_profile

Dependencies
------------

None

Example Playbook
----------------

- hosts: servers 
  gather_facts: no
  user: root
  roles:
  - role: openshift_profile
    op_openshift_profile: 
    - web

License
-------

Apache

Author Information
------------------

Max Whittingham <mwhittingham@redhat.com>
