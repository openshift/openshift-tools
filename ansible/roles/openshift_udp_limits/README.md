openshift_udp_limits
=========

Ansible role for configuring outbound UDP connection limits in Openshift

Requirements
------------


Role Variables
--------------


Dependencies
------------


Example Playbook
----------------

name: "Configure outbound UDP limits"
user: root
hosts: <hosts>
gather_facts: yes
roles:
- tools_roles/openshift_outbound_udp_limits

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
