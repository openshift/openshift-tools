openshift_gcp_add_users_to_project
=========

Ansible role for adding users to a GCP project

Requirements
------------

Ansible Modules: lib_gcloud


Role Variables
--------------

    osgautp_project: GCP project name that users will be added to
    osgautp_user_list: list of user names to be added to the gcp project
    osgautp_email_domain: optional. If this is supplied, this domain will be appended to each
                           user in the user_list
    osgautp_role: the role to add the user to

Dependencies
------------


Example Playbook
----------------
vars:
  user_list:
  - user1
  - user2

  roles:
  - role: tools_roles/openshift_gcp_add_users_to_project
    osgautp_user_list: "{{ user_list }}"
    osgautp_project: projectName
    osgautp_role: roles/editor
    osgautp_email_domain: example.com

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
