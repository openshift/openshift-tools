Role Name
=========

Role to hold steps needed to generate openshift-tools containers.

Requirements
------------

N/A

Role Variables
--------------

base_os: the type of container you want to generate (ie rhel7/centos7)

Dependencies
------------

N/A

Example Playbook
----------------

    - hosts: localhost
      roles:
         - generate_containers
           base_os: rhel7

License
-------

ASL 2.0

Author Information
------------------

Red Hat OpenShift Operations
