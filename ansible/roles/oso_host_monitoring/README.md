# oso_host_monitoring
Applies local host monitoring container(s).

## Requirements

None.

## Role Variables

### osohm_host_name

The human readable name for the host

### osohm_cluster_id

The cluster id of the host from inventory.

### osohm_default_zagg_server_user

Login user for the Zabbix server.

### osohm_default_zagg_server_password

Login password for the Zabbix server

### osohm_docker_registry_ops_email

The email address used with authenticating to the ops registry.

### osohm_docker_registry_ops_key

Text of the key used to authenticate with the ops registry.

### osohm_docker_registry_ops_url

Docker repository containing the monitoring containers.

### osohm_docker_registry_url

The URL used in the systemd service file to pull docker images from.

### osohm_enable_cluster_capacity_reporting

Should cluster capacity reporting be enabled. `True` or `False`

### osohm_environment

The environment tag from inventory.

### osohm_host_monitoring

The name of the host monitoring container

### osohm_host_type

The host type from inventory.

### osohm_sub_host_type

The sub host type from the inventory.

### osohm_master_ha

Is this master part of a highly available configuration. `True` or `False`

### osohm_master_primary

Is this a primary master in a HA configuration

### osohm_monitor_dnsmasq

Should dnsmasq be monitored on the node. `True` or `False`

### osohm_monitor_zabbix_infra

Is Zabbix running on the cluster and should it be monitored? `True` or `False`

### osohm_pruning:

A dictionary of the configuration for the pruning cron job. It has the following keys

```yaml
osohm_pruning:
  cron:
    hour: '*/3'
    minute: '0'
  image_hours_to_keep: '12h'
  image_revisions_to_keep: 5
```

#### cron

A dictionary containing the keys `hour` and `minute` which set the corresponding fields in the cron entry.

#### image_hours_to_keep

The argument passed to the pruning script to have it ignore images younger than set time

#### image_revisions_to_keep

The argument passed to the pruning script indicating the number of image revisions to keep

### osohm_snapshot_aws_access_key_id

The AWS access key to use for the snapshotter

### osohm_snapshot_aws_secret_access_key

The AWS secret access key to use for the snapshotter

### osohm_ops_monitoring_aws_access_key_id

The AWS access key to use for monitoring scripts

### osohm_ops_monitoring_aws_secret_access_key

The AWS secret access key to use for monitoring scripts

### osohm_zagg_client

Name of container with the Zabbix client

### osohm_zagg_verify_ssl

Should the zagg client verify SSL connections. `True` or `False`

### osohm_zagg_web_url

Where to contact the monitoring service.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: servers
  roles:
  - role: tools_roles/oso_host_monitoring
    osohm_host_name: example-master-bf3c3
    osohm_environment: prod
    osohm_host_type: "{{ hostvars[inventory_hostname]['ex_hosttype'] }}"
    osohm_cluster_id: example
    osohm_default_zagg_server_user: "zagg-client"
    osohm_default_zagg_password: "secret"
    osohm_docker_registry_url: "docker-registry.example.com/mon/"
    osohm_docker_registry_ops_url: "https://docker-registry.ops.example.com"
    osohm_docker_registry_ops_key: "OPSEXMAPLEKEY"
    osohm_docker_registry_ops_email: "ops@example.com"
    osohm_enable_cluster_capacity_reporting: True
    osohm_host_monitoring: "oso-rhel7-host-monitoring"
    osohm_master_ha: True
    osohm_master_primary: True
    osohm_monitor_dnsmasq: False
    osohm_pruning:
      cron:
        hour: "*/3"
        minute: "0"
      image_hours_to_keep: "12h"
      image_revisions_to_keep: 5
    osohm_snapshot_aws_access_key_id: "AKIASOMETHING"
    osohm_snapshot_aws_secret_access_key: "awssecretkey"
    osohm_zagg_client: "oso-rhel7-zagg-client"
    osohm_zagg_verify_ssl: True
    osohm_zagg_web_url: "https://..."
```

## Scale Group monitoring

With the introduction to scale groups we will begin to deploy the monitoring container
through a daemonset.  This allows us greater flexibility by removing the requirements
of running specific playbooks at start up and allowing Openshift to deploy the configuration
during the deployment of a daemonset.  This also localizes all of the configuration for
a scale group node to a configmap and secret objects managed by Openshift.

Let's explore what this architecture looks like.  At the current time there are two containers that
will run inside of the daemonset.  The first container will be called config.  The second will be the monitoring
container.

The config container will laydown the necessary configuration
for the monitoring container.  This configuration is kept inside of Openshift inside of a specified
namespace.  This namespace currently defaults to openshift-config.  This namespace is determined by the openshift_daemonset_config role
that lives inside of openshift-ansible.  It can be changed by passing the `openshift_daemonset_config_namespace` variable.

Inside of the `openshift_daemonset_config_namespace` there are a number of important objects.  
- The daemonset is named ops-node-config.
- The configmap is named ops-node-config
- The secret is named ops-node-secret

The daemonset runs on all hosts specified by a specific node-label.  This will be determined by scale group nodes groups.

The configmap holds data regarding the configuration for the nodes.  This currently encompasses:
- ssh keys
- setup of the monitoring-config.yml file required by the monitoring container

The secret will house all of the secret data required.  This currently encompasses:
- docker registry auth

The execution path looks like this:
osohm_host_monitoring role is called with all of the necessary data required to configure monitoring and the daemonset.
The openshift_daemonset_config role from openshift-ansible is in charge of placing all of the data in the correct configmap
and secret.  monitoring-config.yml is generated as well as any of the other necessary data for configuration and is then
passed to openshift_daemonset_config role.  This role manages the daemonset config, secret, and configmap.

Inside of the daemonset config the following operations occur to initialize the monitoring container:
1. The daemonset starts and runs a shell script named: `operations_config.sh`
2. The operations_config.sh will call the configure_host.yml playbook defined in the configmap.
3. The configure_host.yml will configure:
- authorized keys
- docker auth
- setup host monitoring
4. host monitoring container starts and reads the monitoring-config.yml

## License

ASL 2.0

## Author Information

OpenShift operations, Red Hat, Inc
