openshift_volume_provisioner
=========

Ansible role for setting up and configuring the cloud provisioning pod

Due to the nature of Openshift Templates, this role is a one time role and is NOT idempotent.

To clean up from this role, run these commands on a master in the cluster:

```
oc delete template online-volume-provisioner -n openshift-infra
oc delete sa volume-provisioner -n openshift-infra
oc delete ClusterRoleBinding volume-provisioner -n openshift-infra
oc delete ClusterRole volume-provisioner -n openshift-infra
oc delete dc online-volume-provisioner -n openshift-infra
oc delete secret aws-credentials cloud-provider-config -n openshift-infra
```

Requirements
------------

Ansible Modules:

- tools_roles/lib_yaml_editor
- tools_roles/lib_openshift_3.2


Role Variables
--------------

    osvp_provisioner_params:  This is a dict of key values pairs to pass into the provisioner pod.
    osvp_master_nodes: list of master nodes.  This is needed to restart the services, if needed, serially


As of 8-11-16, version openshift-scripts-online-3.2.3.2-1.el7, the valid key value pairs that osvp_provisioner_param
  expects (key name = default value)

```
  NAME=online-volume-provisioner
  IMAGE_PULL_POLICY=IfNotPresent
  IMAGE_NAME
  CLOUD_PROVIDER=aws
  CLOUD_PROVIDER_CONFIG
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  CLUSTER_NAME=kubernetes
  SYNC_PERIOD=1m
  MAX_RETRY_INTERVAL=24h
  RETRY_INTERVAL_UNIT=1m
  MAXIMUM_CAPACITY=1Gi
  MAXIMUM_CLUSTER_CAPACITY=-1Gi
  MAXIMUM_PROJECT_CAPACITY=-1Gi
  TEST_MODE_ENABLED=false
  TEST_FAILURE_RATE=20
  TEST_PROVISIONING_TIME=2s
  LOG_LEVEL=0
```


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
