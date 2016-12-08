Role Name
=========

Ansible role to add or remove instances from and AWS ELB.

Requirements
------------

Ansible Modules:

ec2_elb

python package:
python-boto

Role Variables
--------------

  osaeim_elb_name: name of the elb
  osaeim_instance_ids: LIST of instances to put in ELB
  osaeim_state: state of the instance in the elb
  osaeim_region: region the elb is in


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
