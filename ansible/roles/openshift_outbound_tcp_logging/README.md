openshift_logging
=========

Ansible role for configuring outbound TCP connection logging in Openshift

Requirements
------------


Role Variables
--------------


Dependencies
------------


Example Playbook
----------------

name: "Configure outbound TCP logging"
user: root
hosts: <hosts>
gather_facts: yes
roles:
- tools_roles/openshift_outbound_tcp_logging

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
