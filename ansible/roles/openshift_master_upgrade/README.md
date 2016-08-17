Role Name
=========

Super simple role to upgrade an OpenShift master, including installing specifically Docker 1.9

Requirements
------------

None

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
  - role: openshift_master_upgrade

License
-------

Apache

Author Information
------------------

Max Whittingham <mwhittingham@redhat.com>
