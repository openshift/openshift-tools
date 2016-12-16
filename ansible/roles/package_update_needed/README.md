package_update_needed
=========

Ansible role to test if package needs an update

Requirements
------------

Ansible Modules:

- tools_roles/lib_repoquery


Role Variables
--------------

  pun_package_name: The package (rpm) name to check. This defaults to "atomic-openshift"
  pun_wanted_version: The package version that is wanted.  This will be compared to what is installed
  pun_retval_update_needed: This it the return value from the role that will decide if an upgrade is needed


Dependencies
------------


Example Playbook
----------------
  - role: tools_roles/package_update_needed
    pun_package_name: bash
    pun_wanted_version: 4.2.46-19.el7

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
