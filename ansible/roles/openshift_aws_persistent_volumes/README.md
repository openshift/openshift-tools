openshift_aws_persistent_volumes
=========

Ansible role to create Openshift AWS PV's for Openshift Operations.

Requirements
------------

Ansible Modules:

ec2_vol20

RPM Packages
python package:
python-boto

Role Variables
--------------

  osapv_volumes: volume dict definition of PV's to create

  example:
  osapv_volumes:
  - size: 5
    count: 2
  - size: 1
    count: 3

Dependencies
------------

lib_ansible20

Example Playbook
----------------

- role: ops_roles/openshift_aws_persistent_volumes
  osapv_volumes: "{{ g_pvs }}"


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
