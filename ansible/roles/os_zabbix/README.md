os_zabbix
=========

Automate zabbix tasks.

Requirements
------------

This requires the openshift_tools rpm be installed for the zbxapi.py library.  It can be found here: https://github.com/openshift/openshift-tools under openshift_tools/monitoring/zbxapi.py for now.

Role Variables
--------------

zab_server
zab_username
zab_password
### osohm_enable_cluster_capacity_triggers

Should the triggers for cluster capacity monitoring be enabled on this cluster

Default: `False`

Dependencies
------------

This depeonds on the zbxapi.py library located here: https://github.com/openshift/openshift-tools under openshift_tools/monitoring/zbxapi.py for now.

Example Playbook
----------------

  - zbx_host:
      server: zab_server
      user: zab_user
      password: zab_password
      name: 'myhost'

License
-------

ASL 2.0

Author Information
------------------

OpenShift operations, Red Hat, Inc
