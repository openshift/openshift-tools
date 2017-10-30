openshift_clam_scanner
=========

Ansible role for creating and configuring a ClamAV Signature Updater container

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2


Role Variables
--------------

- `ocavs_namespace`: The project namespace to which the application should be deployed.
- `ocavs_pods_running`: A list of running pods in the project.
- `ocavs_zagg_config`: A dictionary with config data for the ZAGG monitoring client, to populate `zagg_client.yaml`. Expected values: `hostgroups`, `url`, `user`, `password`, `ssl_verify`, `verbose` and `debug`. The value `ocavs_zagg_config.hostgroups` should be a list of host group names.

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
