Role Name
=========

A role that can be used to run oc adm policy to manage groups

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
      name: tools_roles/openshift_group_policy
    vars:
      osgp_namespace: default
      osgp_resource_kind: cluster-role
      osgp_resource_name: system:build-strategy-docker
      osgp_group: system:authenticated
      osgp_state: absent 

License
-------

Apache

Author Information
------------------

OpenShift Operations
