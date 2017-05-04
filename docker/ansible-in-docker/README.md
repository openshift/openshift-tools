ansible-in-docker
=================

Creates dockerfile and scripts to use with ansible scripts to version lock ansible without impacting other work.

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

  - name: "date -u"
    command: /bin/bash -c "date -u"
```
