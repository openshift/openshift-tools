#!/usr/bin/ansible-playbook
---
- hosts: "oo_clusterid_opstest:&oo_version_3:&oo_master_primary"
  gather_facts: no
  user: root

  post_tasks:
  - name: fetch current replica setting
    oc_scale:
      state: list
      name: docker-registry
      namespace: default
    register: scale_out
  #- debug: var=scale_out

  - name: saving replicas
    set_fact:
      original_replicas: "{{ scale_out['results'][0] }}"
  #- debug: var=original_replicas
      
  - name: put new replica setting
    oc_scale:
      state: present
      name: docker-registry
      namespace: default
      replicas: 3
    register: scale_out
  #- debug: var=scale_out

  - pause: seconds=15

  - name: fetch new replica setting
    oc_scale:
      state: list
      name: docker-registry
      namespace: default
    register: scale_out
  #- debug: var=scale_out
  - name: check whether new value applied
    assert:
      that: scale_out['results'][0] == 3

  - name: restore replicas
    oc_scale:
      state: present
      name: docker-registry
      namespace: default
      replicas: "{{ original_replicas }}"
    register: scale_out
  #- debug: var=scale_out
  - name: check whether original value applied
    assert:
      that: scale_out['results'][0] == original_replicas|int

  - name: re-restore replicas
    oc_scale:
      state: present
      name: docker-registry
      namespace: default
      replicas: "{{ original_replicas }}"
    register: scale_out
  - debug: var=scale_out
  - name: check that no changes were made on re-apply
    assert:
      that: scale_out['changed'] == False
