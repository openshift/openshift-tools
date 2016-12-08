openshift_gcp_ssh_keys
=========

Ansible role for adding an ssh keys to a project

Requirements
------------

Ansible Modules: lib_gcloud


Role Variables
--------------

    osgsk_user_list: list of user dicts.

    example:

    osgsk_user_list:
    - username: user1
      pub_key: <ssh key contents>
    - username: user2
      pub_key: <ssh key contents>

Dependencies
------------


Example Playbook
----------------

  - role: tools_roles/openshift_gcp_ssh_keys
    osgsk_user_list: <user_list>

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
