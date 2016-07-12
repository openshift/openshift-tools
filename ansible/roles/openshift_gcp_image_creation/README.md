openshift_gcp_image_creation
=========

Ansible role for adding an imagage tar ball to a project

Requirements
------------

Ansible Modules: lib_gcloud


Role Variables
--------------

    osgic_image_name: name of the image (without .tar.gz)

Dependencies
------------


Example Playbook
----------------

  - role: tools_roles/openshift_gcp_image_creation
    osgic_image_name: centos_7

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
