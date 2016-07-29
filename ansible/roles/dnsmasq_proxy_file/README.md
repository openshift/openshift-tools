Role Name
=========

NOTE: This role assumes that the openshift_node_dnsmasq has been run from the Openshift Installer.
This role was introduced in th Openshift installer 3.2.
This role adds a file to the existing dnsmasq configuration

introduced dnsmasq as part of the install.  This role would overwrite that work.
Please consider the role dnsmasq_proxy_file

Ansible role to use dnsmasq as a dns proxy

Requirements
------------

Role Variables
--------------

  dnsmpf_proxy_map: dns proxy map for dns servers


  Var Examples:

  g_dnsmasq_dns_proxy_map:
  - google.com: 8.8.8.8
  - google.com: 8.8.4.4
  - 10.in-addr.arpa: 10.0.0.1
  - 10.in-addr.arpa: 10.0.0.2

Dependencies
------------


Example Playbook
----------------
- role: 'ops_roles/dnsmasq_proxy_files'
  dnsmpf_proxy_map: "{{ g_dnsmasq_dns_proxy_map }}"

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
