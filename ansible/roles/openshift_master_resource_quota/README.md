openshift_master_storage_class
=========

A role that deploys quotas for Openshift cluster resources

Requirements
------------

None

Role Variables
--------------

osmsc_enable_quotas: BOOL.  Should quotas be enabled.
osmsc_cluster_pv_quota: Cluster wide storage quota
osmsc_exclude_quota_label: labe of the projects that will indicate project is excluded
osmsc_projects_to_exclude: list of projects to exclude from the cluster quota

Dependencies
------------

lib_openshift
lib_yaml_editor

Example Playbook
----------------

- role: tools_roles/openshift_master_resource_quota
  osmsc_enable_quotas: True
  osmsc_cluster_pv_quota: 100Gi
  osmsc_exclude_quota_label: exclude_pv_quota
  osmsc_projects_to_exclude:
  - default
  - openshift-infra


License
-------

Apache

Author Information
------------------

Openshift Operations
