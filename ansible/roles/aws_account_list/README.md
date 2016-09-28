AWS Account List generator
=========

Create list of AWS accounts from ansible inventory.

Requirements
------------

None

Role Variables
--------------

`aal_multi_inventory_location`:
    Path to `multi_inventory.cache`

Dependencies
------------

None

Example Playbook
----------------

    - hosts: bastion
      roles:
        - role: tools_roles/aws_account_list
          aal_multi_inventory_location: /etc/ansible/multi_inventory.yaml

License
-------

ASL 2.0

Author Information
------------------

OpenShift operations, Red Hat, Inc
