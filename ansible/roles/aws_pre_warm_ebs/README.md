aws_pre_warm_ebs
=========

A role that deploys configuratons for Openshift StorageClass

Requirements
------------

None

Role Variables
--------------

apwe_volume: the volume path to "pre warm"

Dependencies
------------


Example Playbook
----------------

- role: tools_roles/aws_pre_warm_ebs
  apwe_volume: /dev/xvda


License
-------

Apache

Author Information
------------------

Openshift Operations
