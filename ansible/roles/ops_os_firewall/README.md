ops_os_firewall
===========

Ops OS Firewall manages  iptable rules


Requirements
------------

lib_os_firewall

Role Variables
--------------

| Name                      | Default |                                        |
|---------------------------|---------|----------------------------------------|
| oof_firewall_allow         | []      | List of dicts of service, port, protocol mappings to allow |
| oof_firewall_deny          | []      | List of dicts of service, port, protocol,  mappings to deny |

Dependencies
------------

lib_aos_modules


Example Playbook
----------------

Use iptables and open tcp ports 80 and 443:
```
---
- hosts: servers
  gather_facts: True
  vars:
    os_firewall_use_firewalld: false
    oof_firewall_allow:
    - service: httpd
      port: 80
      protocol: tcp
    - service: https
      port: 443
      protocol: tcp
  roles:
  - ops_os_firewall
```

License
-------

Apache License, Version 2.0

Author Information
------------------
Openshift Operations
