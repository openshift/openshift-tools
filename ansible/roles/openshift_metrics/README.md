openshift_metrics
=========

Ansible role for setting up and configuring metrics in Openshift

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2
- tools_roles/lib_yaml_editor


Role Variables
--------------

### osamet_node

The number of the cassandra node that is being deployed. Each will need its own
node number to scale up.

Default: `1`

https://github.com/openshift/origin-metrics/blob/master/docs/cassandra_scaling.adoc

Dependencies
------------


Example Playbook
----------------
Use `run_once: true` if the cluster contains multiple masters.

```
  - role: ops_roles/openshift_metrics
    osamet_default_metrics_cert: /path/to/cert
    osamet_default_metrics_key:  /path/to/key
    osamet_default_metrics_cacert: /path/to/cacert
    osamet_clusterid: cluster_id
    osamet_pv_size: pv_size_to_attach
    osamet_masters: list_of_masters
    run_once: true
```

In a separate task, after this role runs, the metrics service can be enabled using the following.

```
- name: Enable metrics
  user: root
  hosts: "oo_clusterid_{{ cli_clusterid }}:&oo_hosttype_master"
  serial: 1
  gather_facts: yes
  tasks:

    - name: Add metrics url to master-config
      yedit:
        src: "/etc/origin/master/master-config.yaml"
        key: assetConfig.metricsPublicURL
        value: "https://metrics.{{ cli_clusterid }}.openshift.com/hawkular/metrics"
        state: present
        backup: False
      register: add_url

    - name: Restart master services if master-config was changed
      service:
        name:
        state: restarted
      when: add_url | changed
      with_items:
      - atomic-openshift-master-api
      - atomic-openshift-master-controllers
```

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
