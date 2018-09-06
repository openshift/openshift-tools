openshift_psad
=========

Ansible role for creating and configuring the psad container and daemonset

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2


Role Variables
--------------

- `psad_namespace`: The project namespace in which the application should be deployed.
- `psad_aws_creds_content`: credentials of the S3 bucket to which we upload files.
- `psad_aws_config_content`: locations of various config and logfiles needed by scanlog_listener.
- `psad_nodes`: Apply the psad=True label to nodes matching value of psad_nodes list.
- `psad_zagg_config`: A dictionary with config data for the ZAGG monitoring client, to populate `zagg_client.yaml`. Expected values: `hostgroups`, `url`, `user`, `password`, `ssl_verify`, `verbose` and `debug`. The value `psad_zagg_config.hostgroups` should be a list of host group names.

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
