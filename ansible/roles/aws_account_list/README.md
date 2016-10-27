AWS Account List generator
=========

Create list of AWS accounts from ansible inventory.

Requirements
------------

None

Role Variables
--------------

`aal_multi_inventory_location`:
    Path to `multi_inventory.yaml`
`aal_multi_inventory_location_legacy`:
    Path to `multi_inventory.yaml` of legacy inventory data
`aal_aws_account_file`:
    Path to output file

Dependencies
------------

None

Example Playbook
----------------

    - hosts: bastion
      roles:
        - role: tools_roles/aws_account_list
          aal_multi_inventory_location: /etc/ansible/multi_inventory.yaml
          aal_multi_inventory_location_legacy: /etc/ansible/multi_inventory.v2.yaml
          aal_aws_account_file: /etc/openshift_tools/aws_accounts.txt

License
-------

ASL 2.0

Author Information
------------------

OpenShift operations, Red Hat, Inc
