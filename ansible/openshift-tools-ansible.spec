Name:           openshift-tools-ansible
Version:        0.0.8
Release:        1%{?dist}
Summary:        Openshift Tools Ansible
License:        ASL 2.0
URL:            https://github.com/openshift/openshift-tools
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:      ansible1.9 >= 1.9.4
Requires:      python2

%description
Openshift Tools Ansible

This repo contains Ansible code and playbooks
used by Openshift Online Ops.

%prep
%setup -q

%build

%install
# openshift-tools-ansible-zabbix install (standalone lib_zabbix library)
mkdir -p %{buildroot}%{_datadir}/ansible/zabbix
cp -rp roles/lib_zabbix/library/* %{buildroot}%{_datadir}/ansible/zabbix/

# openshift-tools-ansible-inventory install
mkdir -p %{buildroot}/etc/ansible
mkdir -p %{buildroot}%{_datadir}/ansible/inventory
mkdir -p %{buildroot}%{_datadir}/ansible/inventory/aws
mkdir -p %{buildroot}%{_datadir}/ansible/inventory/gce
cp -p inventory/multi_inventory.py %{buildroot}%{_datadir}/ansible/inventory
cp -p inventory/multi_inventory.yaml.example %{buildroot}/etc/ansible/multi_inventory.yaml
cp -p inventory/aws/hosts/ec2.py %{buildroot}%{_datadir}/ansible/inventory/aws
cp -p inventory/gce/hosts/gce.py %{buildroot}%{_datadir}/ansible/inventory/gce

# ----------------------------------------------------------------------------------
# openshift-tools-ansible-inventory subpackage
# ----------------------------------------------------------------------------------
%package inventory 
Summary:       Openshift Tools Ansible Inventories
BuildArch:     noarch

%description inventory
Ansible inventories used with the openshift-tools scripts and playbooks.

%files inventory
%config(noreplace) /etc/ansible/*
%dir %{_datadir}/ansible/inventory
%{_datadir}/ansible/inventory/multi_inventory.py*


%package inventory-aws
Summary:       OpenShift Tools Ansible Inventories for AWS
Requires:      %{name}-inventory = %{version}
Requires:      python-boto
BuildArch:     noarch

%description inventory-aws
Ansible inventories for AWS used with the openshift-tools scripts and playbooks.

%files inventory-aws
%{_datadir}/ansible/inventory/aws/ec2.py*

%package inventory-gce
Summary:       OpenShift Tools Ansible Inventories for GCE
Requires:      %{name}-inventory = %{version}
Requires:      python-libcloud >= 0.13
BuildArch:     noarch

%description inventory-gce
Ansible inventories for GCE used with the openshift-tools scripts and playbooks.

%files inventory-gce
%{_datadir}/ansible/inventory/gce/gce.py*

# ----------------------------------------------------------------------------------
# openshift-tools-ansible-zabbix subpackage
# ----------------------------------------------------------------------------------
%package zabbix
Summary:       Openshift Tools Ansible Zabbix library
Requires:      python-openshift-tools-zbxapi
BuildArch:     noarch

%description zabbix
Python library for interacting with Zabbix with Ansible.

%files zabbix
%{_datadir}/ansible/zabbix

%changelog
* Tue May 31 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.8-1
- Rename cluster_group to clusterid (kwoodson@redhat.com)

* Tue May 31 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.7-1
- Fixed a bug with partial creates (kwoodson@redhat.com)
- Fixed create state. (kwoodson@redhat.com)
- Changes to prevent flapping (rharriso@redhat.com)
- Add triggers for low available PVs (rharriso@redhat.com)
- Add trigger to alert when failed persistant volumes are present
  (rharriso@redhat.com)
- Adding cluster_var support. (kwoodson@redhat.com)
- add zabbix entries to hold cluster-wide calculated items (jdiaz@redhat.com)

* Wed May 25 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.6-1
- Yedit bug fixes as well as enhancements (kwoodson@redhat.com)
- bind in host's oc and oadm binaries (so we get 3.1/3.2 bins on 3.1/3.2
  clusters) (jdiaz@redhat.com)
- Added osohm_snapshot_aws_access_key_id and
  osohm_snapshot_aws_secret_access_key to the oso_host_monitoring role.
  (twiest@redhat.com)
- fixed some metrics automations (mwoodson@redhat.com)
- Added update to encompass dict and list.  Added list to return only value
  when key is specified (kwoodson@redhat.com)
- Moved account syntax to a hash (kwoodson@redhat.com)
- pass environment OSO_MASTER_PRIMARY to monitoring container
  (jdiaz@redhat.com)
- Openshift metrics role (kwoodson@redhat.com)
- added openshift_* roles (mwoodson@redhat.com)
- Adding selectors on delete (kwoodson@redhat.com)
- Added decode secret option. Added error handling to oadm_router for when it
  fails (kwoodson@redhat.com)
- Fix to oc_secrets delete_after (kwoodson@redhat.com)
- Added statement to catch errors when creation fails (kwoodson@redhat.com)
- Added name and path to secrets file (kwoodson@redhat.com)

* Mon May 16 2016 Thomas Wiest <twiest@redhat.com> 0.0.5-1
- Added ops-ec2-snapshot-ebs-volumes.py and ops-ec2-trim-ebs-snapshots.py
  (twiest@redhat.com)
- Moving lib_openshift_api to lib_openshift_3.2 (kwoodson@redhat.com)
- Added ops-docker-storage-reinitialize.yml and the sysconfig_fact.py module.
  (twiest@redhat.com)
- update logic to avoid delete/create when updating existing node entries
  (jdiaz@redhat.com)
- Adding 3.2 changes (kwoodson@redhat.com)
- add oc_scale to manage replicas on deploymentconfigs (jdiaz@redhat.com)
- Initial oadm_policy_user (kwoodson@redhat.com)
- add extra group tests and update label tests (jdiaz@redhat.com)
- add group module and extend user module to manage group membership
  (jdiaz@redhat.com)
- added fstab_mount_options (mwoodson@redhat.com)
- Adding exist, append, and add_item (kwoodson@redhat.com)
- add user crud to lib_openshift_api (jdiaz@redhat.com)
- Added cat_fact module. (twiest@redhat.com)
- set dm.basesize to 3G EXTRA_DOCKER_STORAGE_OPTIONS is a no-op on 3.1 clusters
  because docker 1.8's /usr/bin/docker-storage-setup doesn't read/use it. On
  3.2 (docker 1.9) it will not allow container images sizes beyond 3G
  (jdiaz@redhat.com)
- Updated router to take cacert (kwoodson@redhat.com)
- added new docker storage setup options (mwoodson@redhat.com)
- Adding ability to force a refresh on the registry (kwoodson@redhat.com)
- add support for labeling and test cases for labeling nodes specifically
  (jdiaz@redhat.com)
- oc_serviceaccount (kwoodson@redhat.com)
- Bug fixes.  Now accept path or content for certs. (kwoodson@redhat.com)
- oadm_project and oc_route (kwoodson@redhat.com)
- Bug fixes to preserve registry service clusterIP (kwoodson@redhat.com)

* Fri Apr 22 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.4-1
- Kubeconfig fix (kwoodson@redhat.com)
- Refactor. Adding registry helpers.  Adding registry (kwoodson@redhat.com)

* Thu Apr 21 2016 Joel Diaz <jdiaz@redhat.com> 0.0.3-1
- depend on ansible1.9 RPM from EPEL (jdiaz@redhat.com)

* Tue Apr 12 2016 Joel Diaz <jdiaz@redhat.com> 0.0.2-1
- copy filters, inventory, docs and test from openshift-ansible
  (jdiaz@redhat.com)

* Mon Apr 11 2016 Joel Diaz <jdiaz@redhat.com> 0.0.1-1
- new package built with tito

