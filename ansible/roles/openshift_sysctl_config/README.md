openshift_sysctl_config
=========

Ansible role for managing sysctl config settings

Requirements
------------

Ansible Modules:
sysctl


Role Variables
--------------

- `ossc_settings: The sysctl settings to be applied to a node

   settings:
   - name: net.ipv4.ip_forward
     value: 1
     sysctl_file: /etc/sysctl.d/99-sysctl.conf

```
  - include_role:
      name: openshift_sysctl_config
    vars:
      ossc_settings: "{{ my_sysctl_settings }}"
```

See http://docs.ansible.com/ansible/sysctl_module.html for more information.

Dependencies
------------


Example Playbook
----------------

The example role shows how to call and set the net.ipv4.ip_forward=1 sysctl values.

```
#!/usr/bin/ansible-playbook
#---
- hosts: opstest-master-06fe7
  gather_facts: no
  remote_user: root
  vars:
    sysctl_settings:
    - name: net.ipv4.ip_forward
      value: 1
      sysctl_file: /etc/sysctl.d/99-settings.conf
  tasks:
  - include_role:
      name: tools_roles/openshift_sysctl_config
    vars:
      ossc_settings: "{{ sysctl_settings }}"
```

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
