Name:           openshift-tools-ansible
Version:        0.0.11
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

# openshift-tools-ansible-filter-plugins install
mkdir -p %{buildroot}%{_datadir}/ansible_plugins/filter_plugins
cp -p filter_plugins/ops_filters.py %{buildroot}%{_datadir}/ansible_plugins/filter_plugins/ops_filters.py
cp -p filter_plugins/ops_zabbix_filters.py %{buildroot}%{_datadir}/ansible_plugins/filter_plugins/ops_zabbix_filters.py

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

# ----------------------------------------------------------------------------------
# openshift-tools-ansible-filter-plugins subpackage
# ----------------------------------------------------------------------------------
%package filter-plugins
Summary:       Openshift Tools Ansible Filter Plugins
BuildArch:     noarch

%description filter-plugins
Ansible filter plugins used with the openshift-tools

%files filter-plugins
%dir %{_datadir}/ansible_plugins/filter_plugins
%{_datadir}/ansible_plugins/filter_plugins/ops_filters.py*
%{_datadir}/ansible_plugins/filter_plugins/ops_zabbix_filters.py*

%changelog
* Thu Jun 23 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.11-1
- Setting up filter plugins for ops (kwoodson@redhat.com)
- Install python-gcloud. (kwoodson@redhat.com)
- adding pop functionality (kwoodson@redhat.com)
- Changed the thresholds of the established connections as well as critically
  low memory triggers. (twiest@redhat.com)
- Adding instance_states to gce.py (kwoodson@redhat.com)
- random sleep for 5 minutes and run every 4 hours (jdiaz@redhat.com)
- only need to pass one sleep flag (and not 3600 seconds) (jdiaz@redhat.com)
- Adding a 60 sec wait for possible race condition when restarts of services
  occur (kwoodson@redhat.com)
- fixed pylint errors: (mwoodson@redhat.com)
- removed git status (mwoodson@redhat.com)
- added new git modules (mwoodson@redhat.com)
- changing the cron entries, because they were lacking the names and adding
  defattr to files section in one of the packages in the script spec file
  (ihorvath@redhat.com)
- Fixing spacing (mwhittingham@redhat.com)
- Fixing how far it's indented (mwhittingham@redhat.com)
- Fixing handlers name section (mwhittingham@redhat.com)
- Actually fixing yaml syntax (mwhittingham@redhat.com)
- Fixed bug where ec2_tag would run for each master. (twiest@redhat.com)
- Fixed bug where I wasn't passing creds to ec2_tag. (twiest@redhat.com)
- Fixing yaml syntax (mwhittingham@redhat.com)
- Updated ops-docker-loopback-to-direct-lvm.yml to work with our current setup.
  (twiest@redhat.com)
- removed dump extra .com (mwoodson@redhat.com)
- added the postfix_amazon ses client role; updated from address on gpg send
  role (mwoodson@redhat.com)
- Added volume tags to openshift_aws_persistent_volumes (twiest@redhat.com)
- use nodejs-ex instead of nodejs-example for STI test (sten@redhat.com)
- Adding monitoring for existing connections on etcd and master api server
  (ihorvath@redhat.com)
- twiest asked me to change the wording on zagg queue triggers
  (ihorvath@redhat.com)
- Updating to latest gce.py (kwoodson@redhat.com)
- Changed base OS level checks to run every minute so that Jeremy Eder's team
  can use our zabbix data. (twiest@redhat.com)
- Added purpose tag to EBS PV creator. (twiest@redhat.com)
- stop passing in environment variable to host-monitoring container only one
  script uses one of these environment variables (scripts/monitoring/cron-send-
  create-app.py), and the cron job for it is written in a way where the needed
  environment variable is explicitely passed in before launching it
  (jdiaz@redhat.com)
- Removing handlers section from the task section (mwhittingham@redhat.com)
- Fixing spacing for handlers section (mwhittingham@redhat.com)
- Fixing notify handler (mwhittingham@redhat.com)
- Fixing README spacing (mwhittingham@redhat.com)
- Adding notify to template task for service restarts during config changes
  (mwhittingham@redhat.com)
- Creating openshift_dedicated_admin role (mwhittingham@redhat.com)

* Mon Jun 13 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.10-1
- Fixing a bug if get_entry does not contain a key. (kwoodson@redhat.com)
- Made the snapshot and trim operations more error resistant.
  (twiest@redhat.com)
- allow o+rx on openshift_tools (jdiaz@redhat.com)
- change default(False, True) usage to default(False) (jdiaz@redhat.com)
- allow for per-cluster pruning vars (jdiaz@redhat.com)
- added rhmap to image exceptions (sedgar@redhat.com)
- Backup copy to protect ourselves (kwoodson@redhat.com)
- Added ops-ec2-add-snapshot-tag-to-ebs-volumes.py (twiest@redhat.com)
- cleanup of openshft_aws_user (mwoodson@redhat.com)
- move monitoring container configuration into passed-in/bound file Rather than
  pass numerous environment variable to control how the host-monitoring
  container is started/configured, move environment vars into a yaml file that
  can be bound in. This will configure things like the list of cron jobs to
  instantiate, the clusterid, zagg settings, etc. Logic that determines what
  gets installed is moved into the oso-host-monitoring role when it generates a
  monitoring-config.yml file for each node. Config loop will now install
  /etc/openshift_tools/monitoring-config.yml, and the systemd file for host-
  monitoring will bind it in at the same location. (jdiaz@redhat.com)
- Bug fix for first level entries, added append, and fixed update
  (kwoodson@redhat.com)
- cleaned up some new aws account setup roles : (mwoodson@redhat.com)
- add step to remove /etc/sysconfig/docker-storage file old thin pool settings
  in the file can keep docker-storage-setup from working properly
  (jdiaz@redhat.com)
- Updating for dynamic inventory generation (kwoodson@redhat.com)
- more role cleanup (mwoodson@redhat.com)
- added lib_git (mwoodson@redhat.com)
- added module lib_iam_accountid (mwoodson@redhat.com)
- Adding a test for results coming back as None (kwoodson@redhat.com)
- add no log to ssh add keys (mwoodson@redhat.com)
- more fixes for the aws_user (mwoodson@redhat.com)
- Content is now idempotent. (kwoodson@redhat.com)
- added new roles for setting up aws stuff (mwoodson@redhat.com)
- Fixed return val when updating a list (kwoodson@redhat.com)
- Fixed a bug introduced by the deepcopy. Fixed a bug with create.
  (kwoodson@redhat.com)
- detect/enable cluster capacity reporting in the data hierarchy, set
  g_enable_cluster_capacity_reporting to True for any cluster that should have
  this reporting enabled (jdiaz@redhat.com)

* Tue May 31 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.9-1
- Adding snythetic hosts for bootstrapping (kwoodson@redhat.com)
- TDGC: Update vars in example playbook section (whearn@redhat.com)
- Add temp_dir_git_clone (whearn@redhat.com)

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

