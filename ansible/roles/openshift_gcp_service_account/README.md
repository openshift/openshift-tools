openshift_gcp_service_account
=========

Ansible role for creating GCP service accounts

Requirements
------------

Ansible Modules: lib_gcloud


Role Variables
--------------

    osgcpsa_username: Username that will be created
    osgcpsa_display_name: Display name for SA
    osgcpsa_project: GCP Project to use
    osgcpsa_roles: GCP Role to use
    osgcpsa_destination: Path where to write the credentials
    osgcpsa_output_type: Output type to write the file to.  current options: json, multi_inventory
    osgcpsa_output_key_type: can be one of: p12, json

Dependencies
------------


Example Playbook
----------------

  - role: tools_roles/openshift_gcp_service_account
    osgcpsa_username: testuser
    osgcpsa_display_name: Test Service Account
    osgcpsa_project: testproject
    osgcpsa_roles: roles/viewer
    osgcpsa_destination: /tmp/
    osgcpsa_output_type: multi_inventory
    osgcpsa_output_key_type: p12

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
