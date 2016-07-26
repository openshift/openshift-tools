lib_aos_modules
=========

A role containing modules that are needed for Ops configuration


the aos_firewall_manage_iptables module.  This is copied from upstream:

https://github.com/openshift/openshift-ansible/blob/master/roles/os_firewall/library/os_firewall_manage_iptables.py

Requirements
------------

None

Example Playbook
----------------

To make sure that we can reference these modules, include a role as such:

    - hosts: servers
      roles:
         - lib_aos_modules

License
-------

Apache

