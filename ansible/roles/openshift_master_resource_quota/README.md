openshift_master_resource_quota
=========

A role that deploys quotas for Openshift cluster resources

Requirements
------------

None

Role Variables
--------------

osmrq_enable_quotas: BOOL.  Should quotas be enabled.
osmrq_cluster_pv_quota: Cluster wide storage quota
osmrq_exclude_quota_label: labe of the projects that will indicate project is excluded
osmrq_projects_to_exclude: list of projects to exclude from the cluster quota

Dependencies
------------

lib_openshift
lib_yaml_editor

Example Playbook
----------------

- role: tools_roles/openshift_master_resource_quota
  osmrq_enable_quotas: True
  osmrq_cluster_pv_quota: 100Gi
  osmrq_exclude_quota_label: exclude_pv_quota
  osmrq_projects_to_exclude:
  - default
  - openshift-infra


License
-------

Apache

Author Information
------------------

Openshift Operations
