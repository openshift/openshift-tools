openshift_master_resource_quota
=========

A role that deploys quotas for Openshift cluster resources

Requirements
------------

None

Role Variables
--------------

osmrq_enable_pv_quotas: BOOL.  Should pv quotas be enabled.
osmrq_enable_service_lb_quotas: BOOL.  Should service loadbalancer quotas be enabled.
osmrq_cluster_pv_quota: Cluster wide storage quota
osmrq_cluster_service_lb_quota: Cluster wide service loadbalancer quota
osmrq_exclude_pv_quota_label: label that will indicate project is excluded from PV quota
osmrq_exclude_service_lb_quota_label: label that will indicate project is excluded from service loadbalancer quota
osmrq_pv_projects_to_exclude: list of projects to exclude from the cluster pv quota
osmrq_service_lb_projects_to_exclude: list of projects to exclude from the cluster service loadbalancer quota

Dependencies
------------

lib_openshift
lib_yaml_editor

Example Playbook
----------------

- role: tools_roles/openshift_master_resource_quota
  osmrq_enable_pv_quotas: True
  osmrq_cluster_pv_quota: 100Gi
  osmrq_exclude_pv_quota_label: exclude_pv_quota
  osmrq_pv_projects_to_exclude:
  - default
  - openshift-infra


License
-------

Apache

Author Information
------------------

Openshift Operations
