Role Name
=========

The purpose of this role is to add cluster specific stats to zabbix. These are stats that are added directly to hosts in the OpenShift cluster, instead of to templates as they need to reference data from other hosts in the cluster.

This is useful, for example, for computed items.

Requirements
------------

lib_zabbix

Role Variables
--------------

  ozcs_infra_nodes: The infrastructure nodes of the cluster
  ozcs_primary_master: The primary master of the cluster
  ozcs_zbx_server: The zabbix server in which to create the items
  ozcs_zbx_user: The zabbix user with which to authenticate
  ozcs_zbx_password: The zabbix password with which to authenticate


Dependencies
------------

lib_zabbix

Example Playbook
----------------

    - hosts: servers
      roles:
         - role: os_zabbix_cluster_stats
           ozcs_zbx_server: http://localhost/zabbix/api_jsonrpc.php
           ozcs_zbx_user: Admin
           ozcs_zbx_password: zabbix
           ozcs_primary_master: cid-master-07f3e
           ozcs_infra_nodes:
           - cid-node-infra-2d7f7
           - cid-node-infra-d1f9a

License
-------

ASL 2.0

Author Information
------------------

Thomas Wiest
