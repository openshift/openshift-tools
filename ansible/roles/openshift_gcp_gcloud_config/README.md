openshift_gcp_gcloud_config
=========

Ansible role for adding an configuring gcloud config

Requirements
------------

Ansible Modules: lib_gcloud


Role Variables
--------------

    osggc_project: sets gcloud to use the project
    osggc_region: sets gcloud to use the region


Dependencies
------------


Example Playbook
----------------

  - role: tools_roles/openshift_gcp_gcloud_config
    osggc_project: test-project
    osggc_region: us-east1

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
