openshift_logging
=========

Ansible role for preparing an image

Requirements
------------

Ansible Modules:


Role Variables
--------------
oap_package_list: List of packages to install in the base image

Dependencies
------------


Example Playbook
----------------
  - role: tools_roles/openshift_ami_prep
    oap_package_list: "{{ list_of_packages }}"

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
