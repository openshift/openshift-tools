Role Name
=========

A role that can be used to run the reconciler which will update the policies stored in etcd for the cluster.

Requirements
------------

None

Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------

- hosts: servers
  gather_facts: no
  user: root
  roles:
  - role: openshift_reconcile_cluster_roles

License
-------

Apache

Author Information
------------------

Max Whittingham <mwhittingham@redhat.com>
