Role Name
=========

A role that deploys packages and configs nessacary to setup the OpenShift Dedicated Admin role.

Requirements
------------

None

Role Variables
--------------

  oda_ded_admin_users: A list of users to set as OpenShift Dedicated Admins

Dependencies
------------

None

Example Playbook
----------------

    - hosts: servers
      roles:
         - role: openshift_dedicated_admin
	   oda_ded_admin_users:
	   - user1
           - user2	


License
-------

Apache

Author Information
------------------

Max Whittingham <mwhittingham@redhat.com>
