OpenShift Ansible Inventory
=========

Install and configure openshift-tools-scripts-inventory-clients.

Requirements
------------

None

Role Variables
--------------

oo_inventory_group
oo_inventory_user
oo_inventory_accounts
oo_inventory_cache_max_age
oo_rsync_cache_targets - array of hosts to rsync inventory cache to
oo_rsync_cache_target_user - user on target hosts used for rsync
oo_rsync_cache_target_dir - directory on target hosts to write inventory cache file
oo_rsync_private_key - contents of the private key needed for rsync over ssh

Dependencies
------------

None

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

ASL 2.0

Author Information
------------------

OpenShift operations, Red Hat, Inc
