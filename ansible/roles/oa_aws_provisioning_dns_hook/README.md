oa_aws_provisioning_dns_hook
=========

This is a special ansible role that is meant to be used with openshift-ansible.  This role provides a "hook" and can be passed in to the openshift-ansible via the the openshift-ansible variable

"openshift_aws_custom_dns_provider_role"

This role doesn't follow the pattern of other roles because it's being called from a run with openshift-ansible.


Requirements
------------

openshift-ansible

python-dyn python module


Role Variables
--------------

These variables also must be set with the openshift ansible variables

oa_dyn_customer_name
oa_dyn_user_name
oa_dyn_password


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
