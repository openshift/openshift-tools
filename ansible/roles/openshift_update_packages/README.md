openshift_update_packages
=========

Ansible role to update Openshift packages based on a version number

Requirements
------------

Ansible Modules:

- tools_roles/lib_repoquery


Role Variables
--------------

  osup_update_type: This is the type of Openshift node to update.  Choices are "master" or "node"
  osup_version:  The version to upgrade to
  osup_node_packages:  List of packages for the node to update.  This is set to a default list in defaults/main.yml
  osup_master_packages: List of packages for the master to update.  This is set to a default list in defaults/main.yml


Dependencies
------------


Example Playbook
----------------

  - role: tools_roles/openshift_update_packages
    osup_update_type: master
    osup_version: 3.2.1.17-1.git.0.6d01b60.el7

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
