openshift_template_deployer
=========

Generic Template Deployer - Ansible generic role for setting up and deploying templates

Requirements
------------


Role Variables
--------------

  ostd_rpm: optional: rpms to install prior to template creation
  ostd_template_name: name of template
  ostd_template_file: name of template file
  ostd_project: project name
  ostd_template_edits: key/value pairs of edits needed for template
  ostd_template_params: key/value pairs of paramaters to supply to the template file. Params are formated in the style of:
```
   PARAM_1 : VALUE_1
```


Dependencies
------------

Ansible Modules:

- "aos_{{ g_play_openshift_version }}_roles/lib_utils"
- "aos_{{ g_play_openshift_version }}_roles/lib_openshift"


Example Playbook
----------------

- name: Test add
  hosts: "oo_clusterid_cicd:&oo_version_3:&oo_master_primary"
  gather_facts: no
  remote_user: root
  tasks:
  - include_role:
      name: tools_roles/openshift_template_deployer
    vars:
      ostd_rpm: other_needed_rpm
      ostd_template_name: template_name
      ostd_template_file: path_to_template_file.yml
      ostd_project: project_name
      ostd_template_edits:
      - key: key_value_1
        value: value_1
      ostd_template_params:
        PARAM_1 : VALUE_1

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
