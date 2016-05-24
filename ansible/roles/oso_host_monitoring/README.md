Role Name
=========

Applies local host monitoring container(s).

Requirements
------------

None.

Role Variables
--------------

osohm_zagg_web_url: where to contact monitoring service
osohm_host_monitoring: name of host monitoring container
osohm_zagg_client: name of container with zabbix client
osohm_docker_registry_url: docker repository containing above containers
osohm_default_zagg_server_user: login info to zabbix server
osohm_default_zagg_password: password to zabbix server
osohm_snapshot_aws_access_key_id: The AWS access key to use for the snapshotter
osohm_snapshot_aws_secret_access_key: The AWS secret access key to use for the snapshotter

Dependencies
------------

None.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      vars:
        osohm_zagg_web_url: "https://..."
        osohm_host_monitoring: "oso-rhel7-host-monitoring"
        osohm_zagg_client: "oso-rhel7-zagg-client"
        osohm_docker_registry_url: "docker-registry.example.com/mon/"
        osohm_default_zagg_server_user: "zagg-client"
        osohm_default_zagg_password: "secret"
        osohm_snapshot_aws_access_key_id: "AKIASOMETHING"
        osohm_snapshot_aws_secret_access_key: "awssecretkey"
      roles:
      - oso_host_monitoring

License
-------

ASL 2.0

Author Information
------------------

OpenShift operations, Red Hat, Inc
