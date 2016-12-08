Role Name
=========

NOTE: This should NOT be used anymore.  The openshift installer 3.2
introduced dnsmasq as part of the install.  This role would overwrite that work.
Please consider the role dnsmasq_proxy_file

Ansible role to use dnsmasq as a dns proxy

Requirements
------------

Role Variables
--------------

  dnsmp_original_nameserver: original DNS server that dnsmasq will use as default
  dnsmp_proxy_map: dns proxy map for dns servers


  Var Examples:

  g_dnsmasq_original_nameserver: 4.2.2.2
  g_dnsmasq_dns_proxy_map:
  - google.com: 8.8.8.8
  - google.com: 8.8.4.4
  - 10.in-addr.arpa: 10.0.0.1
  - 10.in-addr.arpa: 10.0.0.2

Dependencies
------------


Example Playbook
----------------
- role: 'ops_roles/dnsmasq_proxy'
  dnsmp_original_nameserver: "{{ g_dnsmasq_original_nameserver }}"
  dnsmp_proxy_map: "{{ g_dnsmasq_dns_proxy_map }}"

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
