openshift_udp_limits
=========

Ansible role for configuring outbound UDP connection limits in Openshift

Requirements
------------


Role Variables
--------------

`oudp_node_name`: The node name (must agree with the node name shown via `oc nodes`)

`oudp_node_ip`: The node's main network interface IP address (its private IP address in AWS and GCP)

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
