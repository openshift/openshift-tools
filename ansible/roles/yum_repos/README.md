Yum Repos
=========

This role allows easy deployment of yum repository config files.

Requirements
------------

Yum or dnf

Role Variables
--------------

yr_yum_cert_content: yum certificate content
yr_yum_key_content: yum certificate key content
yr_yum_cert_dir: Location to place yum certificates
yr_yum_repo_list: List of dictionaries representing a yum repository


Dependencies
------------

Example Playbook
----------------

- role: tools_roles/yum_repos
  oyr_yum_cert_content: "{{ client_cert_content }}"
  oyr_yum_key_content: "{{ client_key_content }}"
  oyr_yum_repo_list: "{{ yum_repos }}"

License
-------

ASL 2.0

Author Information
------------------

openshift online operations
