openshift_logging
=========

Ansible role for setting up and configuring logging in Openshift

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_api
- tools_roles/lib_yaml_editor


Role Variables
--------------


Dependencies
------------


Example Playbook
----------------
  - role: tools_roles/openshift_logging
    osalog_default_logging_cert: /path/to/cert
    osalog_default_logging_key:  /path/to/key
    osalog_default_logging_cacert: /path/to/cacert
    osalog_clusterid: cluster_id
    osalog_es_cluster_size: number_of_elastic_search
    osalog_pv_size: pv_size_to_attach
    osalog_node_count: node_count
    osalog_masters: list_of_masters

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
