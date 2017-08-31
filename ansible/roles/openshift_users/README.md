Role Name
=========

A role that can be used to run to manage OpenShift users. This is useful to provision users without having to go through official sign up / billing workflows.

Requirements
------------

None

Role Variables
--------------

osu_usernames - a list of usernames to provision.
osu_provider - Name of the authentication provider to set for the usernames passed in. This should match one of the oauth providers in master-config.yml.

Dependencies
------------

openenshift_ansible's lib_openshift library

Example Playbook
----------------

- hosts: servers
  gather_facts: no
  remote_user: root
  tasks:
  - include_role:
      name: tools_roles/openshift_user_policy
    vars:
      osu_usernames:
      - bill
      - someuser
      osu_provider: redhat-sso


License
-------

Apache

Author Information
------------------

OpenShift Operations
