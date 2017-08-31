Role Name
=========

A role that can be used to run oc adm policy to manage users

Requirements
------------

None

Role Variables
--------------

None

Dependencies
------------

openenshift_ansible's lib_openshift library

Example Playbook
----------------

- hosts: servers
  gather_facts: no
  remote_user: root
  tasks:
  - include_role:
      name: tools_roles/openshift_user_policy
    vars:
      osup_user_policy_bindings:
      - user: bill
        resource_kind: cluster-role
        resource_name: cluster-reader

      - user: someuser
        namespace: default
        resource_kind: cluster-role
        resource_name: system:build-strategy-docker
        state: absent


License
-------

Apache

Author Information
------------------

OpenShift Operations
