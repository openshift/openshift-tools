openshift_master_storage_class
=========

A role that deploys configuratons for Openshift StorageClass

Requirements
------------

None

Role Variables
--------------

osmsc_storageclass_name: Name of the storage class to create
osmsc_storageclass_provisioner: The kubernetes provisioner to use
osmsc_storageclass_type: type of storage to use. This is different among clouds/providers
osmsc_enable_quotas: BOOL.  Should quotas be enabled.
osmsc_cluster_pv_quota: Cluster wide storage quota
osmsc_exclude_quota_label: labe of the projects that will indicate project is excluded
osmsc_projects_to_exclude: list of projects to exclude from the cluster quota

Dependencies
------------

lib_openshift_3.2
lib_yaml_editor

Example Playbook
----------------

- role: tools_roles/openshift_master_storage_class
  osmsc_storageclass_name: awsEBS
  osmsc_storageclass_provisioner: kubernetes.io/aws-ebs
  osmsc_storageclass_type: gp2
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
