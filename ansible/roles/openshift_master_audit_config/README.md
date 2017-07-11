openshift_master_audit
=========

Ansible role for configuring the audit capabilities on OpenShift masters.

Optional parameters not defined will be removed from master-config.yaml if
present.

https://docs.openshift.org/latest/install_config/master_node_configuration.html#master-node-config-audit-config

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2
- tools_roles/lib_yaml_editor


Role Variables
--------------

### omac_enabled

Enable/disable the OpenShift master audit log.

Default: `False`

### omac_auditConfig_auditFilePath

File path where the requests should be logged to. If not set, logs will be printed to master logs.

### omac_auditConfig_maximumFileRetentionDays

Specifies maximum number of days to retain old audit log files based on the timestamp encoded in their filename.

### omac_auditConfig_maximumRetainedFiles

Specifies Maximum number of old audit log files to retain.

### omac_auditConfig_maximumFileSizeMegabytes

Specifies maximum size in megabytes of the log file before it gets rotated.

Dependencies
------------


Example Playbook
----------------
  - role: tools_roles/openshift_master_audit
    omac_auditConfig_enabled: False
    omac_auditConfig_auditFilePath: "/var/log/openshift-master-audit.log"
    omac_auditConfig_maximumFileRetentionDays: 30
    omac_auditConfig_maximumRetainedFiles: 30
    omac_auditConfig_maximumFileSizeMegabytes: 100

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
