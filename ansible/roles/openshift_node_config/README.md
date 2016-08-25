Role Name
=========

A role to modify the OpenShift node configuration

Requirements
------------

None

Role Variables
--------------

onc_openshift_node_config: Any changes needed to be made to the config file. Values must be what the config file is expecting.

Dependencies
------------

None

Example Playbook
----------------

- hosts: servers 
  roles:
  - role: openshift_node_config
    onc_openshift_node_config:
    - key: OPENSHIFT_PROFILE
      value: web

License
-------

Apache

Author Information
------------------

Max Whittingham <mwhittingham@redhat.com>
