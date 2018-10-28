#!/bin/bash

# do the prereqs
/usr/bin/ansible-playbook -i /tmp/inventory.yml /usr/share/ansible/openshift-ansible/playbooks/aws/openshift-cluster/prerequisites.yml

# do the provision
/usr/bin/ansible-playbook -i /tmp/inventory.yml /usr/share/ansible/openshift-ansible/playbooks/aws/openshift-cluster/provision_install.yml

# setup the cluster auth
/usr/bin/ansible-playbook -i /tmp/inventory.yml /opt/openshift-tools/ansible/playbooks/release/openshift_cluster_auth.yml

