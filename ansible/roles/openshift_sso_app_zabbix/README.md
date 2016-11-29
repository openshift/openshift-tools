openshift_sso_app
=========

Ansible role for adding a Zabbix aggregate item and trigger to the ops-aws-synthetic host

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2


Role Variables
--------------

- `ossoz_zbx_server`: The name of the Zabbix server
- `ossoz_zbx_user`: The user with which to authenticate to the Zabbix server
- `ossoz_zbx_password`: The password of the user
- `ossoz_clusterid`: The id of the cluster

Dependencies
------------


Example Playbook
----------------


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
