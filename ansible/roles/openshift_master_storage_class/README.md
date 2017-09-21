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

Dependencies
------------

lib_openshift
lib_yaml_editor

Example Playbook
----------------

- role: tools_roles/openshift_master_storage_class
  osmsc_storageclass_name: awsEBS
  osmsc_storageclass_provisioner: kubernetes.io/aws-ebs
  osmsc_storageclass_type: gp2

License
-------

Apache

Author Information
------------------

Openshift Operations
