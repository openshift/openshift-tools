openshift__namespace_settings
=========

Ansible role for Openshift V3 Secured Router

Requirements
------------

Ansible Modules:

- lib_openshift


Role Variables
--------------

ossr_default_router_certs: list of paths to the router cert files
ossr_default_router_keys: corresponding list of paths to the router key files (in same order as ossr_default_router_certs)
ossr_default_router_cacert: path to chain certificate file for the certs/keys above
ossr_routers: list of router objects with router configuration details per router
ossr_cloud: one of aws or gcp that the OpenShift router is being configured for (will pull in cloud-specific router settings)

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
