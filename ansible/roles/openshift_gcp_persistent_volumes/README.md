openshift_gcp_persistent_volumes
=========

Ansible role to create Openshift GCP PV's for Openshift Operations.

Requirements
------------

Ansible Modules:

lib_gcloud

Role Variables
--------------

  osapv_volumes: volume dict definition of PV's to create
  osgpv_sublocation: region in gcp
  osgpv_zone: zone in gcp
  osgpv_account: gcp account
  osgpv_clusterid: gcp clusterid


  example:
  osapv_volumes:
  - size: 5
    count: 2
  - size: 1
    count: 3

Dependencies
------------

lib_ansible20

Example Playbook
----------------

- role: ops_roles/openshift_gcp_persistent_volumes
  osapv_volumes: "{{ g_pvs }}"
  osgpv_sublocation: "{{ oo_sublocation }}"
  osgpv_zone: "{{ g_gcp_zone }}"
  osgpv_account: "{{ oo_account }}"
  osgpv_clusterid: "{{ oo_clusterid }}"



License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
