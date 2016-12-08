Role Name
=========

A role that deploys packages and configs nessacary to setup the OpenShift Dedicated Admin role.

Requirements
------------

None

Role Variables
--------------

 oda_config: Any changes needed to be made to the config file. Values must be what the config file is expecting (e.g. a comma delimited list of dedicated admin users).
 oda_service_enabled: Whether or not the openshift-dedicated-role service should be enabled at boot
 oda_service_started: Whether or not the openshift-dedicated-role service should be running currently

Dependencies
------------

None

Example Playbook
----------------

- hosts: servers
  roles:
  - role: openshift_dedicated_admin
    oda_service_enabled: true
    oda_service_running: true
    oda_config:
    - key: SKIP_PROJECTS
      value: default,openshift-infra
    - key: USERS
      value: user1,user2


License
-------

Apache

Author Information
------------------

Max Whittingham <mwhittingham@redhat.com>
