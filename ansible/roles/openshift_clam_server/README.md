openshift_clam_server
=========

Ansible role for creating and configuring the clam-scanner container and daemonset

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2


Role Variables
--------------

- `oii_namespace`: The project namespace in which the application should be deployed.
- `oii_aws_creds_content`: credentials of the S3 bucket containing the clam signature files.
- `oii_aws_config_content`: locations of various config and logfiles needed by pull_clam_signatures.
- `oii_nodes`: Apply the clam-server-enabled=True label to nodes matching value of ocs_nodes list.

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
