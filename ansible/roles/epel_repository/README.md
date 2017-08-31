Role Name
=========

Install the EPEL repository RPM file

Requirements
------------

N/A

Role Variables
--------------

epelr_exclude: A space-separated list of packages that should not be pulled from EPEL.
epelr_skip_if_unavailable: Bool.  will set the "skip_if_unavailable" to the repo file. Defaults to true

Dependencies
------------


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - ops_roles/epel_repository

License
-------

ASL 2.0

Author Information
------------------

OpenShift Online Ops
