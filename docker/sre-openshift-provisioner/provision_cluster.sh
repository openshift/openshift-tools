#!/bin/bash -e

# do the prereqs
/usr/bin/ansible-playbook -i /tmp/inventory.yml /usr/share/ansible/openshift-ansible/playbooks/aws/openshift-cluster/prerequisites.yml

# do the provision
/usr/bin/ansible-playbook -i /tmp/inventory.yml /usr/share/ansible/openshift-ansible/playbooks/aws/openshift-cluster/provision_install.yml

# setup the cluster auth and other post auth settings
/usr/bin/ansible-playbook -i /tmp/inventory.yml /opt/openshift-tools/ansible/playbooks/release/openshift_cluster_post_install_config.yml

# for now, olm is optional
install_olm=$(awk -F: '/operator_lifecycle_manager_install/{print $2}' /tmp/inventory.yml | tr 'A-Z' 'a-z' | tr -d ' ')

if [ ${install_olm} = 'true' ]; then
  /usr/bin/ansible-playbook -i /tmp/inventory.yml /opt/openshift-tools/ansible/playbooks/release/olm.yml
fi
