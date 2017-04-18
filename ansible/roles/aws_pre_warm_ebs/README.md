aws_pre_warm_ebs
=========

A role that "pre-warms" an EBS volume.

More info can be found here:

http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-initialize.html

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
