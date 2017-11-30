openshift_clam_scanner
=========

Ansible role for creating and configuring the image-inspector container and daemonset

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2


Role Variables
--------------

- `oii_namespace`: The project namespace in which the application should be deployed.
- `oii_aws_creds_content`: credentials of the S3 bucket to which we upload files.
- `oii_aws_config_content`: locations of various config and logfiles needed by scanlog_listener.
- `oii_nodes`: Apply the image-inspector-enabled=True label to nodes matching value of oii_nodes list.
- `oii_zagg_config`: A dictionary with config data for the ZAGG monitoring client, to populate `zagg_client.yaml`. Expected values: `hostgroups`, `url`, `user`, `password`, `ssl_verify`, `verbose` and `debug`. The value `oii_zagg_config.hostgroups` should be a list of host group names.

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
