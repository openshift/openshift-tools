ansible-in-docker
=================

Creates dockerfile and scripts to use with ansible scripts to version lock ansible without impacting other work.

TODO:
* enable centos/rhel container builds .. see other container builds for pattern
* Best way to install generated scripts to /usr/bin/. ?
* We need to build and push to registry.ops.openshift.com so that both tower machines are using the exact same images.
* Need to use epel / el7 specific RPM versions.
* Add deprecation section to alert the user when the version of ansible being used has been deprecated.

Usage:

* build.bash
* use built scripts in `#!` line in ansible script

test.yaml:

```
#!./oso-ansible-playbook-2.3.0.0-3
# - or -
#!./oso-ansible-playbook-2.2.2.0-1

- hosts: my-host
  remote_user: root
  gather_facts: false

  tasks:

  - name: show the ansible version
    debug: var=ansible_version
```
