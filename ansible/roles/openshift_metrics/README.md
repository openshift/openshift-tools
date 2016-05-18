openshift_metrics
=========

Ansible role for setting up and configuring metrics in Openshift

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2
- tools_roles/lib_yaml_editor


Role Variables
--------------


Dependencies
------------


Example Playbook
----------------
  - role: ops_roles/openshift_metrics
    osamet_default_metrics_cert: /path/to/cert
    osamet_default_metrics_key:  /path/to/key
    osamet_default_metrics_cacert: /path/to/cacert
    osamet_clusterid: cluster_id
    osamet_pv_size: pv_size_to_attach
    osamet_masters: list_of_masters

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
