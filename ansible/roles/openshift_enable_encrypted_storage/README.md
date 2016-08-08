openshift_enable_encrypted_storage
=========

Ansible role for storing encrypted storage setting for a cluster

Requirements
------------

Ansible Modules:


Role Variables
--------------

osees_directory: directory for where the role should place the yaml file that records the fact that the cluster should have encrypted storage

Dependencies
------------


Example Playbook
----------------

  - role: tools_roles/openshift_enable_encrypted_storage
    osees_directory: "/var/lib/git/repo/{{ clusterid }}/"


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
