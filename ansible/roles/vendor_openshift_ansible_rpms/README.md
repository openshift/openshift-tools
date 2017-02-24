Vendor Openshift Ansible RPMS
=========

This role takes a list of openshift-ansible rpms and explodes them into an ouput directory

Requirements
------------

An existing dir of RPMS

Role Variables
--------------

vosar_output_directory: Directory where to explode the openshift-ansible-rpms
vosar_rpm_directory: The directory where the openshift-ansible rpms are located

Dependencies
------------

Example Playbook
----------------

- role: tools_roles/vendor_openshift_ansible_rpms
  vosar_rpm_directory: /tmp/openshift-ansible-rpms
  vosar_output_directory: /tmp/openshift-ansible

License
-------

ASL 2.0

Author Information
------------------

Openshift Operation
