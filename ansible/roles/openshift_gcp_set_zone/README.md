openshift_gcp_service_account
=========

Ansible role for fetching a list of zones from GCP, then writing one out to a specified location

Requirements
------------

Ansible Modules: lib_gcloud, lib_yaml_editor


Role Variables
--------------

    osgcpsz_output_dir: Output dir to write the zone to. writes to the <dir>/main.yml
    osgcpsz_region: region in GCP to query for zones


Dependencies
------------


Example Playbook
----------------

```

  - role: tools_roles/openshift_gcp_set_zone
    osgcpsz_output_dir: /tmp/gcp_zone
    osgcpsz_region: us-east1

```

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
