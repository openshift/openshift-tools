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

### osohm_zagg_client

Name of container with the Zabbix client

### osohm_zagg_verify_ssl

Sould the zagg client verify SSL connections. `True` or `False`

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

## License

ASL 2.0

## Author Information

OpenShift operations, Red Hat, Inc
