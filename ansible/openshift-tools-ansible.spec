Name:           openshift-tools-ansible
Version:        0.0.72
Release:        1%{?dist}
Summary:        Openshift Tools Ansible
License:        ASL 2.0
URL:            https://github.com/openshift/openshift-tools
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:      ansible
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
cp -p inventory/aws/ec2.py %{buildroot}%{_datadir}/ansible/inventory/aws
cp -p inventory/gce/gce.py %{buildroot}%{_datadir}/ansible/inventory/gce

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
* Tue Nov 12 2019 Matt Woodson <mwoodson@redhat.com> 0.0.72-1
- Add key for fluentd queue check (nbauer@redhat.com)
- Update trigger for dedicated-admin-operator (sedgar@redhat.com)
- Fix http_failed triggers (sedgar@redhat.com)
- fixed the route 200 zabbix trigger (mwoodson@redhat.com)
- Add data points and alerts for app curl failures (sedgar@redhat.com)
- add zabbix key and trigger for new check (bmeng@redhat.com)
- add cronjob for the new admin jks cert check (bmeng@redhat.com)
- force sync attempt (dranders@redhat.com)
- Resolves missing name:default label Cluster provisioning was occurring with
  the `name:default` label missing from the default namespace. This caused user
  created projects to fail due to the reliance on this label by the `allow-
  from-default-namespace` NetworkPolicy. (dofinn@redhat.com)
- updated the ssl check to accept the hosts from being passed into the role
  (mwoodson@redhat.com)
- added 2 more guardduty rules to the customer admin role (mwoodson@redhat.com)
- updated the customer admin access policy (mwoodson@redhat.com)
- fixed the registry ip docker cert dir role (mwoodson@redhat.com)
- fixed the registry ip fix (mwoodson@redhat.com)
- raise the priority of the exsiting checks (bmeng@redhat.com)
- skip the teminating pod check on online free clusters (bmeng@redhat.com)
- added the openshift registry ip cert role (mwoodson@redhat.com)
- added route53 resolver rules customeradmin policy for BYOC
  (mwoodson@redhat.com)
- remove the check for the un-used path/cert for internal ssl
  (bmeng@redhat.com)
- added createvpcendpoint and describevpcendpoint to the byoc customer admin
  policy (mwoodson@redhat.com)
- added the RAM to the customeradmin policy for BYOC (mwoodson@redhat.com)
- alert on elasticsearch cluster in red state (dranders@redhat.com)
- Enable monitoring container to see cluster tier (sedgar@redhat.com)
- template error (dranders@redhat.com)
- es in red state zabbix average alert (dranders@redhat.com)
- Fix triggers for node counts (nbauer@redhat.com)
- Add triggers for node counts (nbauer@redhat.com)
- Fix indentation (nbauer@redhat.com)
- Add cron for node count check (nbauer@redhat.com)
- Update cron check frequency (nbauer@redhat.com)
- Update template_openshift_master.yml (nbauer@redhat.com)
- Update template_openshift_master.yml (nbauer@redhat.com)
- Fixing item order (nbauer@redhat.com)
- Add node count keys to zabbix vars (nbauer@redhat.com)
- Add node count to monitoring config (nbauer@redhat.com)
- remove logging check from reg-aws for this cluster didn't have logging
  (zhizhang@redhat.com)
- add trigger for ds (zhizhang@redhat.com)
- make the monitoring daemonset always pull on restart to ensure latest
  monitoring pod (mwoodson@redhat.com)
- using openshift repos (haowang@redhat.com)
- add cronjob and zabbix trigger for terminating pod check (bmeng@redhat.com)
- add monitor item for snapshot tags (haowang@redhat.com)
- Add snapshot tag check script to rpm and cronjob (haowang@redhat.com)
- add checks for logging check script (zhizhang@redhat.com)
- revert changes (zhizhang@redhat.com)
- add high alert for logging ops-runner (zhizhang@redhat.com)
- Bump the project check priority (haowang@redhat.com)
- add cronjob for fluentd and configpod (zhizhang@redhat.com)
- fix trigger for dedicated admin check (zhizhang@redhat.com)
- Revert "Adjust Zabbix alert thresholds for ES disks"
  (dak1n1@users.noreply.github.com)
- Added zabbix check for dedicated-admin-operator (sedgar@redhat.com)
- Adjust Zabbix alert thresholds for ES disks (sedgar@redhat.com)
- fix a typo in cronjob (bmeng@redhat.com)
- Update the alert priority of autoapprover and metrics server pods
  (haowang@redhat.com)
- add cronjob and zabbix key for the console check script (bmeng@redhat.com)
- add trigger for zabbix check (zhizhang@redhat.com)
- add cronjob for zabbix check (zhizhang@redhat.com)
- add zabbix monitor status check script (zhizhang@redhat.com)
- zabbix_data_sync: Don't assume hostgroup is present
  (mbarnes@fedoraproject.org)
- add ansible role zabbix_data_sync (zhizhang@redhat.com)
- Add dns resolution timeout monitor item (haowang@redhat.com)
- Add zabbix monitor item (haowang@redhat.com)
- build script into rpm (haowang@redhat.com)
- update trigger time (dranders@redhat.com)
- Fix the logging alert so that it clears at 20%% (sedgar@redhat.com)
- Only alert after ES does automated disk balancing (sedgar@redhat.com)
- Improve readability by using Markdown formatting
  (18159+lisa@users.noreply.github.com)
- enable ssl internal check again (zhizhang@redhat.com)
- tmp remove internel check of ssl (zhizhang@redhat.com)
- add_ca_file (dranders@redhat.com)
- change level from avg to high for dedicated-admin service trigger
  (zhizhang@redhat.com)
- add trigger for the openshift-dedicated-admin service (zhizhang@redhat.com)
- add monitoring for dedicated-admin service (zhizhang@redhat.com)
- change ssl check from avg to high (zhizhang@redhat.com)
- add cron job for Internal ssl check (zhizhang@redhat.com)
- SREP-1064: short term fix to pin origin-ansible to a known good version
  (nmalik@redhat.com)
- make config pod tolerate everything (haowang@redhat.com)
- Revert "change router-health check to high alert" (mbarnes@fedoraproject.org)
- Add an item for openshift.master.atomic-openshift.version in zabbix
  (bmorriso@redhat.com)
- add avg alert on the public ssl check by http (zhizhang@redhat.com)
- bugfix for the item ssl (zhizhang@redhat.com)
- add zabbix item for ssl check (zhizhang@redhat.com)
- fix the key name (zhizhang@redhat.com)
- add cron job for the ssl expire info by http hearder (zhizhang@redhat.com)
- working around oc_obj limitation (dedgar@redhat.com)
- change router-health check to high alert (dranders@redhat.com)
- add_etcd_volume: Support M4 instances (mbarnes@fedoraproject.org)
- fixed some config loop of fetching zagg ip (mwoodson@redhat.com)
- Adding openshift_node_group role from openshift-ansible's release-3.11 branch
  (bmorriso@redhat.com)
- add_etcd_volume.yml: Add some recommended comments
  (mbarnes@fedoraproject.org)
- Add adhoc playbook: add_etcd_volume.yml (mbarnes@fedoraproject.org)
- Only run devaccess tasks on nodes that have a devaccess user
  (bmorriso@redhat.com)
- Tiered access for scalegroup nodes (bmorriso@redhat.com)
- updated the sre first boot script insights to register with the cluster name
  and node type (mwoodson@redhat.com)
- adding roles and files for new containers - these will watch node journals
  for new container creation events (PLEG) and log them to a PV
  (dedgar@redhat.com)
- splitting rkhunter into its own container with monitoring (dedgar@redhat.com)
- cloud_storage_udev_rules: Rename "sd*" devices to "xvd*"
  (mbarnes@fedoraproject.org)
- updated to non fail (mail@rafaelazevedo.me)
- fixed format strings (mail@rafaelazevedo.me)
- code needs to be aster client is made (mail@rafaelazevedo.me)
- added logic that tells us cert is already applied (mail@rafaelazevedo.me)
- module to update cert id on elb (mail@rafaelazevedo.me)
- Enable alerts for autoapprover and metrics-server (haowang@redhat.com)
- Add tolerations to openshift-config DaemonSet (haowang@redhat.com)
- Adjusted customer-admin access based on vpc peering tests via federated role
  (nmalik@redhat.com)
- Added openshift_aws_iam_byoc role (nmalik@redhat.com)
- Add zabbix item and cronjob for pod check (haowang@redhat.com)
- updated the lib_openshift link (mwoodson@redhat.com)
- Update lib_openshift (gburges@redhat.com)
- setup-etcd-volume.sh: Simplify (mbarnes@fedoraproject.org)
- os_utils: Remove nvme-cli package (mbarnes@fedoraproject.org)
- cloud_storage_udev_rules: Tweaks for RHEL 7 (mbarnes@fedoraproject.org)
- only select az if it can support required instance types (tparikh@redhat.com)
- Add cloud_storage_udev_rules (mbarnes@fedoraproject.org)
- Fix fqdns (tfahlman@redhat.com)
- Handle multiple infra elbs if multiple are defined (tfahlman@redhat.com)

* Mon Jan 14 2019 Alex Chvatal <achvatal@redhat.com>
- actually define the dns resolution timeout key (achvatal@redhat.com)
- trigger an average alert if there's a dns timeout within 3 minutes
  (achvatal@redhat.com)

* Thu Oct 11 2018 Drew Anderson <dranders@redhat.com> 0.0.70-1
- 

* Wed Oct 10 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.69-1
- added lib_openshift_ansible_utils to roles (mwoodson@redhat.com)
- Copy .docker/config.json in kubelet location (jupierce@redhat.com)

* Mon Oct 01 2018 Kenny Woodson <kwoodson@redhat.com> 0.0.68-1
- make fluentd/node mismatch triggers a warning (achvatal@redhat.com)
- include the psad vars and correct the trigger (achvatal@redhat.com)
- Do not update sublocation for synthetic_hosts. (kwoodson@redhat.com)
- os_zabbix: fixed up the zabbix server db checks (mwoodson@redhat.com)
- Updated triggering filesystem metrics in grow_root_vg playbooks
  (nmalik@redhat.com)
- Updates to grow var script for m5: (nmalik@redhat.com)
- Fix URL for "Openshift Node process not running on {HOST.NAME}"
  (mbarnes@fedoraproject.org)
- Updated grow_root_vg-m5.yml to reserve 5000 sectors (nmalik@redhat.com)
- Added adhoc script to grow rootvg (var) for m5 nodes. (nmalik@redhat.com)
- adding ignore_errors statement (dedgar@redhat.com)
- adding files and role for psad container (dedgar@redhat.com)
- Updated disable HT verification (nmalik@redhat.com)
- Add role to optionally disable hyper-threading at runtime.
  (nmalik@redhat.com)
- Make quotas removable. Actually make quotas role run_once. Don't restart
  master services (bmorriso@redhat.com)
- de-prio node label alert, it's storming (gburges@redhat.com)
- Add alert rule for docker grpc (haowang@redhat.com)
- Add monitor item for docker grpc issue (haowang@redhat.com)
- add trigger for node label check (zhizhang@ovpn-12-38.pek2.redhat.com)
- Changed oo_rsync_private_key to be the key, not a path to the key
  (nmalik@redhat.com)
- Refactored how ansible_inventory manages known_hosts (nmalik@redhat.com)
- extend the resource quota role to support service LBs (bmorriso@redhat.com)
- Switched to using command with ssh-keyscan to populate known_hosts for rsync
  (nmalik@redhat.com)
- update ansible_inventory to setup known_hosts for rsync targets
  (nmalik@redhat.com)
- Fix mode for rsync key used to copy inventory cache (nmalik@redhat.com)
- ansible_inventory ssh key name changed to be more specific
  (nmalik@redhat.com)
- ansible_inventory rsync to non-root user and target dir is variable
  (nmalik@redhat.com)
- Fixing rsync for ansible_inventory (nmalik@redhat.com)
- add item for zabbix of node.label (zhizhang@zhizhangdeMacBook-Pro.local)
- Merging rsync into inventory.sh (ansible_inventory role) (nmalik@redhat.com)
- Updated ansible_inventory to support rsync of cache to multiple target hosts
  (nmalik@redhat.com)
- add docker grpc check (haowang@redhat.com)
- add checks for label of all the host on a cluster
  (zhizhang@ovpn-12-41.pek2.redhat.com)
- Add k8s node labels to BYO generator template (bmorriso@redhat.com)
- name in zabbix should match inventory (ihorvath@redhat.com)
- added more robust error checking and debug messages (sedgar@redhat.com)
- removing docker template from ansible-tower nodes (ihorvath@redhat.com)
- changing regex to work on 3.10 also (ihorvath@redhat.com)
- Add support for arbitrary values, not just cluster id (bmorriso@redhat.com)
- Add filter_plugin to generate kubernetes AWS tag (bmorriso@redhat.com)

* Thu Jul 26 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.67-1
- fixing some problems in host monitoring (ihorvath@redhat.com)

* Wed Jul 25 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.66-1
- fixed quota resource role to be idempotent for 3.9; ensured 3.7 works as well
  (mwoodson@redhat.com)
- added gather_facts to no on scalegroup pod (mwoodson@redhat.com)
- fixed generate byo to include node group var on each node type
  (mwoodson@redhat.com)
- docker_storage_to_overlay2: Stop and restart API service
  (mbarnes@fedoraproject.org)
- fixed an ses var naming bug (mwoodson@redhat.com)
- fix the same trigger name error for logging (zhizhang@redhat.com)
- syntax error (achvatal@redhat.com)
- 1 minute not 1 hour for the eviction trigger (achvatal@redhat.com)
- actually track and notify based on the eviction data collected
  (achvatal@redhat.com)
- docker_storage_to_overlay2: Allow setting overlay2.size explicitly
  (mbarnes@fedoraproject.org)
- track evictions from the event stream (achvatal@redhat.com)
- added a rsyslog restarter to scale group config pods to overcome rsyslog bug
  (mwoodson@redhat.com)
- ops-docker-loopback-to-direct-lvm.yml: Load docker_storage_setup defaults
  (mbarnes@fedoraproject.org)
- ops-docker-loopback-to-direct-lvm.yml: Update the template file name
  (mbarnes@fedoraproject.org)
- docker registry try, take 2 (mwoodson@redhat.com)
- added docker registry symlinker in the daemoneset config loop pod thingy
  (mwoodson@redhat.com)
- catching edge case where rec_js['results']['description'] key does not exist
  (dedgar@redhat.com)

* Mon Jun 18 2018 Matthew Barnes <mbarnes@fedoraproject.org> 0.0.65-1
- multi_inventory.py: Fix handling of boolean values
  (mbarnes@fedoraproject.org)
- adding role for iam account list (dedgar@redhat.com)

* Wed Jun 13 2018 Matthew Barnes <mbarnes@redhat.com>
- multi_inventory.py: Ensure boolean groups exist (mbarnes@redhat.com)
- monitoring: added the hyperkube as a valid option for node process count
  (mwoodson@redhat.com)
- disabled the cron-send-security-updates checks from the host-monitoring
  container (mwoodson@redhat.com)
- missed the region for one of the modified scripts (ihorvath@redhat.com)
- use the default version of iam_cert, since we no longer need a custom library
  (sedgar@redhat.com)
- Include playbooks/aws and playbooks/gce in vendored openshift-ansible
  (bmorriso@redhat.com)
- Correct typo and set subnet AZ for vpc (bmorriso@redhat.com)

* Thu May 31 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.63-1
- guess not every cron syntax is usable (ihorvath@redhat.com)

* Thu May 31 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.62-1
- changing logging in snapshot related parts (ihorvath@redhat.com)
- Fixed a bug with active media strings. (kwoodson@redhat.com)
- change the check from every 5 minutes to every 1 minutes because of the ELB
  bug (zhizhang@redhat.com)
- Changed metadata for the bastion host rename. (twiest@redhat.com)
- yum_repos: Ensure reposdir is default path (mbarnes@fedoraproject.org)

* Wed May 23 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.61-1
- ansible tower monitoring has no need for oc binary (ihorvath@redhat.com)
- we need to not delete certain roles from openshift-ansible when we vendor
  (mwoodson@redhat.com)
- changing some things around cluster cap, also doing some housecleaning around
  dockerfile, maybe abolish some layers this way (ihorvath@redhat.com)
- Changed frequency of openshift.master.dnsmasq.curl.status
  (mail@rafaelazevedo.me)
- wrong path for cron command (ihorvath@redhat.com)
- cases matter (ihorvath@redhat.com)

* Thu Apr 19 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.60-1
- oops, there was already a script with the same name, renaming to oc-cluster-
  capacity (ihorvath@redhat.com)
- adding the podpsec to the monitoring container and adding it to cron
  (ihorvath@redhat.com)

* Thu Apr 19 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.59-1
- adding cluster capacity to zabbix (ihorvath@redhat.com)
- changing the webconsole check to not alert on flapping (ihorvath@redhat.com)
- workflow updates (dedgar@redhat.com)
- rm double quotes (dyocum@redhat.com)
- docker_storage_to_overlay2.yml: Use local roles (mbarnes@fedoraproject.org)
- Add docker_storage_to_overlay2 role (mbarnes@fedoraproject.org)
- Add docker_storage_driver_role (mbarnes@fedoraproject.org)
- added sleep values for the snapshotter (mwoodson@redhat.com)
- forgot the host name from alert, hard to know where it came from without it
  (ihorvath@redhat.com)
- fix 1 week notschedulable trigger (sten@redhat.com)
- work-around for tsb_selector (dyocum@redhat.com)
- final step for web checks (ihorvath@redhat.com)
- fixing zabbix templates from stg-to-prod mess (ihorvath@redhat.com)
- adding the zabbix trigger and item for the webconsole check
  (ihorvath@redhat.com)
- reduce trigger severity for immediate node not schedulable to info, send a
  high alert when node not schedulable is current state and has been for over a
  week (sten@redhat.com)
- trigger on <30, 20 %% free, not <70, 80 (sten@redhat.com)
- Adapt ops-docker-storage-reinitialize.yml for overlay
  (mbarnes@fedoraproject.org)
- fixing conflict in stg with ntp (mwoodson@redhat.com)
- fixed ntp -> ntpd (mwoodson@redhat.com)
- Reduce the requested CPU by half, move to 1.5*1024 for memory
  (peter.portante@redhat.com)
- [WIP]adding clam update container (#2845) (dedgar@redhat.com)
- Add adhoc playbook docker_storage_to_overlay2.yml (mbarnes@fedoraproject.org)
- Revert "Merge pull request #2962 from mbarnes/docker_storage_to_overlay2_stg"
  (mbarnes@fedoraproject.org)
- Add adhoc playbook docker_storage_to_overlay2.yml (mbarnes@fedoraproject.org)
- updated the chrony role to install ntp, but disable it as opposed to removing
  ntp (mwoodson@redhat.com)
- change name: to gp2 to match openshift-ansible upstream name
  (dyocum@redhat.com)
- Increasting the sensitivy of the docker storage check (mmahut@redhat.com)
- Update main.yml (wesley.s.hearn@gmail.com)
- that extra line (dyocum@redhat.com)
- "Revert" (dyocum@redhat.com)
- v2 (dyocum@redhat.com)
- Update main.yml (yocum@redhat.com)
- added logic to update OS when os_update is defined (dyocum@redhat.com)
- just set os_upgrade - no need to set it to "True" (dyocum@redhat.com)
- added when: logic to os_update_latest (dyocum@redhat.com)
- add openshift_disk_provision role (#2741) (blentz@users.noreply.github.com)
- Revert "Patching comparison operation breaking with iptables lock message is
  …" (joelsmith@users.noreply.github.com)
- Patching comparison operation breaking with iptables lock message is present
  in output (dedgar@redhat.com)
- resolving conflict (dedgar@redhat.com)
- update all links to ops-sop (blentz@redhat.com)
- Remove the reference to k8s flatten hash (peter.portante@redhat.com)
- Use oc_volume to add the router configmap volume. (bbarcaro@redhat.com)
- Raising critical memory alert priority to high (bmorriso@redhat.com)
- change the metrics check to check on the last 2 value (zhizhang@zhizhang-
  laptop-nay.redhat.com)

* Mon Apr 02 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.58-1
- monitor actual http response code from kibana (sten@redhat.com)
- docker storage set: allow package to be passed in (mwoodson@redhat.com)
- tsb needs "{u'type': u'infra'}" format, not 'type=infra' (dyocum@redhat.com)
- re-ordered a line, ensure that we pull logging and metrics images from the
  correct registry (dyocum@redhat.com)
- just moved a line to the right place (dyocum@redhat.com)
- added template_service_broker_selector='type=infra' (dyocum@redhat.com)
- hardcode the image prefix for components into the byo template
  (dyocum@redhat.com)
- should be obg_location should be gce for o-a compliance (dyocum@redhat.com)
- Revert "should be gcp, not gce" (dyocum@redhat.com)
- adding retries to git_clone - sometimes github doesn't answer on the first
  call (dyocum@redhat.com)
- should be gcp, not gce (dyocum@redhat.com)
- added (dyocum@redhat.com)
- added obg_install_registry_console to defaults (dyocum@redhat.com)
- adding obg_registry_console_variables to pass in vars to the cockpit-ui role
  (dyocum@redhat.com)
- added vars to inventory for: (dyocum@redhat.com)
- adding web_console var to openshift_byo_generator (dyocum@redhat.com)
- adding web_console section to byo template (dyocum@redhat.com)
- Removing crio bind mounts. (kwoodson@redhat.com)
- router cert byo template - remove openshift_hosted_router_certificate
  (bmorriso@redhat.com)
- set default SDN to redhat/openshift-ovs-networkpolicy in byo defaults
  (dyocum@redhat.com)

* Tue Mar 06 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.57-1
- Adding ELB config support to generate BYO role (bmorriso@redhat.com)
- Adding back files which were moved. (kwoodson@redhat.com)
- Adding autokeys, rootlog, and organization to daemonset config.
  (kwoodson@redhat.com)
- pagerduty setup in zabbix-server (ihorvath@redhat.com)
- adding missing dir from openshift-ansible rpms (dyocum@redhat.com)
- INC0686625 - add udp/31685 and tidy up other rules (dbaker@redhat.com)
- service catalog and associated components aren't ready for prime time, yet.
  Disabling (dyocum@redhat.com)
- only trigger high when 10+%% of nodes are not ready, otherwise trigger
  average (sten@redhat.com)

* Wed Feb 14 2018 Drew Anderson <dranders@redhat.com> 0.0.56-1
- Adding crio mounts to crio containers to enable monitoring.
  (kwoodson@redhat.com)
- Fixing format to json (kwoodson@redhat.com)
- do the pull before the kill (dranders@redhat.com)
- specifying port 443 (dyocum@redhat.com)
- renamed all registry.ops.openshift.com to registry.reg-aws.openshift.com
  registry.ops.openshift.com has been shutdown and the cname removed
  (dyocum@redhat.com)
- Adding enhancements to handle large files in configmaps.
  (kwoodson@redhat.com)
- Updating variable to point at correct roles. (kwoodson@redhat.com)
- Updating host monitoring for scale groups (kwoodson@redhat.com)
- Adding package to tower package list. (kwoodson@redhat.com)

* Tue Jan 30 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.55-1
- changing registry for zagg-web (ihorvath@redhat.com)

* Tue Jan 30 2018 Sten Turpin <sten@redhat.com> 0.0.54-1
- added option for service catalog (sedgar@redhat.com)
- correct new ES check key names to match keys being sent from check script
  (sten@redhat.com)
- updated openshift.logging.elasticsearch.disk_free_pct from 70 to 30
  (zhiwliu@redhat.com)

* Mon Jan 29 2018 Sten Turpin <sten@redhat.com> 0.0.53-1
- moved symlink of lib_openshift from 3.6 to 3.7 (mwoodson@redhat.com)
- to work around jinja2 defined test for gcs even if the variable is set to
  NULL, simply having the key present means it's defined (dyocum@redhat.com)
- added the docker options to the byo gen template (mwoodson@redhat.com)
- tested working on devenv (sten@redhat.com)
- send disk as %% free instead of used + freE (sten@redhat.com)
- Vendor files directory of openshift-ansible (jupierce@redhat.com)
- Revert "Vendor files dir from ansible" (jupierce@redhat.com)
- Vendor files dir from ansible (jupierce@redhat.com)
- remove the trigger before we have sop for this (zhizhang@zhizhang-laptop-
  nay.redhat.com)
- Remove references to outdated scheduler configs (sedgar@redhat.com)
- Stop managing fullName for openshift users. The IDP fills this in, and we're
  not asking for it when we grant tiered access. (twiest@redhat.com)
- cmds needs to be separated into args (sedgar@redhat.com)
- /usr/bin/oadm does not exist in OCP 3.8 (sedgar@redhat.com)
- lftp to nodes, because it's useful (gburges@redhat.com)
- no copying gcs user keyfile from private_vars to tmp setup_user
  (dyocum@redhat.com)
- no need to copy obg_gcp_user_gcsdockerregistry_file to obg_user_dir the full
  path is being set in o-a-ops generate_byo_inventory.yml (dyocum@redhat.com)
- try copy, again (dyocum@redhat.com)
- copy: isn't working, neither is cp (dyocum@redhat.com)
- debug a bit (dyocum@redhat.com)
- copy the gcp_user_gcsdockerregistry.yml to /tmp/<user>/ to be used by the
  byo-inventory (dyocum@redhat.com)
- don't copy and convert - the problem isn't in the byo, it MIGHT be in how the
  gcskeyfile is being created in o-a-tools libs. (dyocum@redhat.com)

* Thu Jan 11 2018 Justin Pierce <jupierce@redhat.com> 0.0.52-1
- fix mis-spell in logging check script and add trigger for the logging es
  cluster (zhizhang@zhizhang-laptop-nay.redhat.com)
- use variable for namespace (dedgar@redhat.com)
- updated the vendor openshift ansible role to support 3.8 and also support
  previous versions (mwoodson@redhat.com)
- moving var includes to tech profile (dedgar@redhat.com)
- updating includes (dedgar@redhat.com)
- need some logic to set the destination file for gcs keyfile ONLY when we're
  installing on GCS (dyocum@redhat.com)
- fixes to address pylint, @drewandersonnz and @portante reviews
  (sten@redhat.com)
- grow_root_vg, tested on ded-stage-aws and online-stg (sten@redhat.com)
- Add pylint disable (dbaker@redhat.com)
- Fix indent (dbaker@redhat.com)
- renamed filter plugins to have different names. needed for 2.4
  (mwoodson@redhat.com)
- Handle presumed data structure change of incidents; permit proper matching of
  past incidents in order to update or close them (dbaker@redhat.com)
- fixing some new openshift-3.8 vendoring issues (mwoodson@redhat.com)
- changed storageclass name gcppd to standard to match upstream openshift-
  ansible (dyocum@redhat.com)
- add python2-cryptography rpm for ansible 2.4 (jdiaz@redhat.com)
- change the app create to the primary master (zhizhang@zhizhang-laptop-
  nay.redhat.com)
- extrack rpms from openshift ansible -- leave the rpms around for now
  (mwoodson@redhat.com)
- add a when to copy and convert gcs keyfile task (dyocum@redhat.com)
- set a default obg_gcp_user_gcsdockerregistry_file for non-gce clusters
  (dyocum@redhat.com)
- rm dest_gcsdockerregistry_file if it exists (dyocum@redhat.com)
- enable ROUTER_USE_PROXY_PROTOCOL=True (dyocum@redhat.com)
- remove extra crap (dyocum@redhat.com)
- typo (dyocum@redhat.com)
- convert gcs user key from  yaml to json with a python one-liner and make it
  available in /tmp/$USER (dyocum@redhat.com)
- try local_action: copy: (dyocum@redhat.com)
- seems ugly to cat in, echo out to convert yaml to json, but let's try it
  (dyocum@redhat.com)
- ignore_errors to see the error. :p (dyocum@redhat.com)
- debug the copy/convert (dyocum@redhat.com)
- wrong indentation (dyocum@redhat.com)
- copying the obg_gcp_user_gcsdockerregistry_file from the o-a-private to tmp
  dir, converting from yaml to json (dyocum@redhat.com)
- changed obg_gce_gcs_keyfile to obg_registry_storage_gcs_keyfile
  (dyocum@redhat.com)
- fixed a typo (dyocum@redhat.com)
- added support for gcs bucket for debug purposes, the wait_for_pod registry
  check should not fail and halt the rest of the cluster component installation
  (dyocum@redhat.com)
- added more regions to the copy script (mwoodson@redhat.com)
- update tbyo generator template (mwoodson@redhat.com)
- cleaning up (dedgar@redhat.com)
- fixing node name (dedgar@redhat.com)
- fixing node name (dedgar@redhat.com)
- adding clam scanner pod (dedgar@redhat.com)
- another cleanup of ntp/chrony (mwoodson@redhat.com)
- fixed ntp for gcp (don't remove ntp, just disable it (mwoodson@redhat.com)
- updated "edits" section for correctness (dyocum@redhat.com)
- credentials changed to kubeconfig (dyocum@redhat.com)
- added docker registry rate limiting to new cluster installs
  (mwoodson@redhat.com)

* Thu Nov 16 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.51-1
- Add early log/drop for udp 80 traffic (dbaker@redhat.com)
- Avoid bug where scripts rpm automatically updates (sedgar@redhat.com)
- add docker and atomic-openshift-node memory reporting (jdiaz@redhat.com)
- add cron job to report cgroup slice mem metrics (jdiaz@redhat.com)
- adding the region to the snapshot related commands in crontab
  (ihorvath@redhat.com)

* Wed Nov 08 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.50-1
- Only check pv usage on dedicated clusters (bmorriso@redhat.com)

* Wed Nov 08 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.49-1
- add cgroup memory usage metrics (jdiaz@redhat.com)
- reorder discovery items (jdiaz@jdiaz-t450.lan)
- Reduce the requested CPU by half, move to 1.5*1024 for memory
  (peter.portante@redhat.com)
- gcloud is deprecated google-cloud-sdk is correct (dyocum@redhat.com)
- no .master. either (sten@redhat.com)
- rename projects -> project for consistency and so calculation actually
  happens (sten@redhat.com)
- changing host monitoring source registry (ihorvath@redhat.com)
- stop storage alert flapping (jdiaz@redhat.com)
- include cluster name with alert (jdiaz@redhat.com)
- fixed typo 50 -> 60 (sten@redhat.com)
- add project count delta trigger (sten@redhat.com)
- list_addresses requires 'region' now (dyocum@redhat.com)
- missed a spot (dyocum@redhat.com)
- put it back in the non-private func (dyocum@redhat.com)
- don't need to pass region to the result func (dyocum@redhat.com)
- old versions of gcloud api didn't need --region=<region> to 'describe' an
  address, now it does. (dyocum@redhat.com)
- removed unsupported register.rc bits added region, now required by gcloud
  (dyocum@redhat.com)
- changed ebs to gp2 (dyocum@redhat.com)

* Fri Oct 27 2017 Kenny Woodson <kwoodson@redhat.com> 0.0.48-1
- Making group whitelisting easier. (kwoodson@redhat.com)
- gcp lb takes a while to come alive - let's wait 2 minutes and keep trying
  every 6s (dyocum@redhat.com)
- zabbix server partitioning bits (mwoodson@redhat.com)
- fix the trigger name for re issue (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix autoheal for high alert (zhizhang@zhizhang-laptop-nay.redhat.com)
- add auto-heal for heartbeat.ping (zhizhang@zhizhang-laptop-nay.redhat.com)
- roles/docker_storage_setup: Support overlay2 (mbarnes@fedoraproject.org)
- adding clam update container (dedgar@redhat.com)
- Revert "Clam update container (#2997)" (dedgar@redhat.com)
- Clam update container (#2997) (dedgar@redhat.com)

* Tue Oct 17 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.47-1
- Removing all groups except all_hosts and oo_ (kwoodson@redhat.com)
- adding the new cli option to the running config (ihorvath@redhat.com)

* Mon Oct 16 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.46-1
- allow world read for the multi_inventory.cache file (jdiaz@redhat.com)
- chattr recursively, or we get blocked on rm
  /var/lib/docker/volumes/metadata.db (sten@redhat.com)
- Removing duplicate snapshot trim call. (kwoodson@redhat.com)
- fix syntax in docker role (sedgar@redhat.com)
- start docker on boot (sedgar@redhat.com)
- add support for registry auth to byo generator (sedgar@redhat.com)
- Script re-write * remove test code * use logger * use library functions
  OCUtil * check Deployment Config * show caught errors from curl function *
  verbosity levels * rename smal to saml (dranders@redhat.com)
- text in quotes (dyocum@redhat.com)
- addded some spaces to make it look pretty (dyocum@redhat.com)
- better task name (dyocum@redhat.com)
- added     state: "{{ item.state | default(present)}}" (dyocum@redhat.com)

* Tue Sep 26 2017 Kenny Woodson <kwoodson@redhat.com> 0.0.45-1
- Fix for inventory on v2. (kwoodson@redhat.com)
- fixed some dependencies for lib_openshift roles (mwoodson@redhat.com)
- monitor certs in /etc/etcd (sten@redhat.com)
- removed include lib_openshift from tasks (dyocum@redhat.com)
- renamed osmsc_ vars to osmrq_ (dyocum@redhat.com)
- rewrote README for resource_quota (dyocum@redhat.com)
- splitting out clusterresourcequotas from storageclasses role
  (dyocum@redhat.com)
- set the default to False (dyocum@redhat.com)
- changed oul_os_update to type bool (dyocum@redhat.com)

* Tue Sep 19 2017 Kenny Woodson <kwoodson@redhat.com> 0.0.44-1
- stop checking customer pods storage utilisation (dranders@redhat.com)
- fix the auto heal from HEAL to Heal (zhizhang@zhizhang-laptop-nay.redhat.com)
- Proper escaping in zabbix (mmahut@redhat.com)
- changed HEAL to Heal (zhiwliu@redhat.com)
- added HEAL for the trigger (zhiwliu@redhat.com)
- removing deprecated logrotate option (dedgar@redhat.com)
- fixes requested by jdiaz (sten@redhat.com)
- added cron-send-router-reload-time check (sten@redhat.com)

* Mon Sep 11 2017 Kenny Woodson <kwoodson@redhat.com> 0.0.43-1
- Fixed a bug in gce_ variable. (kwoodson@redhat.com)

* Mon Sep 11 2017 Kenny Woodson <kwoodson@redhat.com> 0.0.42-1
- Adding oo_name as the default to the inventory display name.
  (kwoodson@redhat.com)
- oc_adm_project doesn't exist in lib_openshift. switching to oc_project
  (dedgar@redhat.com)
- Fix include_role (whearn@redhat.com)
- Raising EBS alert severity back to high (bmorriso@redhat.com)
- add timeout to drain step (sedgar@redhat.com)
- lower severity of EBS volumes stuck in attaching to average for the weekend
  (bmorriso@redhat.com)
- Tech Debt: Migrate to new lib_openshift (whearn@redhat.com)
- added option to specify package name (sedgar@redhat.com)
- add symlink to roles dir (sedgar@redhat.com)
- add update script for RHEL 7.4 (sedgar@redhat.com)

* Mon Aug 21 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.41-1
- add retries to openshift_aws_group to avoid failures due to api rate limiting
  (blentz@redhat.com)
- obg_kmskeyid is omitted which means it is defined (jdiaz@redhat.com)
- clean up docs (blentz@redhat.com)
- fix pylint issues (blentz@redhat.com)
- Exclude yum update when not updating (whearn@redhat.com)
- rename module to lib_aws_service_limit (blentz@redhat.com)
- create aws_service_limit module (blentz@redhat.com)

* Wed Aug 09 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.40-1
- Set a default to false for generate certificate for hosted router
  (kwoodson@redhat.com)
- Changed openshift_user_policy and openshift_users to only run once.
  (twiest@redhat.com)
- Added openshift_users role. (twiest@redhat.com)
- adding version check for proper storage api (ihorvath@redhat.com)
- moving the limits, it was in the wrong section in the template
  (ihorvath@redhat.com)
- Updating to 3.6 lib_openshift (whearn@redhat.com)
- add openshift_disk_provision role (#2748) (blentz@users.noreply.github.com)
- Changed openshift_user_policy to take a list of cluster role bindings instead
  of a single one. (twiest@redhat.com)
- Adding necessary config to run and report rkhunter scans from host monitoring
  container (dedgar@redhat.com)

* Wed Jul 19 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.39-1
- counting services (ihorvath@redhat.com)
- add var that can disable app create on special clusters (ihorvath@redhat.com)
- fix typo (ihorvath@redhat.com)
- remove quotes around the description (dyocum@redhat.com)
- Revert "adding zone so config loop won't fail" (dyocum@redhat.com)
- Revert moving to lib_openshift for existing roles (whearn@redhat.com)
- changed oc_secret_add to oc_serviceaccount_secret (dyocum@redhat.com)
- adding zone so config loop won't fail (ihorvath@redhat.com)
- fixed a typo (dyocum@redhat.com)
- lib_openshift migration: oadm -> oc_adm (whearn@redhat.com)
- Adding eu-west-2 to our ami copy. (kwoodson@redhat.com)
- remove the heal for docker_storage_low (zhiwliu@redhat.com)
- changed tag_Name to oo_name so that this playbook can also run on gcp hosts
  (zhiwliu@redhat.com)
- remove average heal for low docker storage (zhiwliu@redhat.com)
- added HEAL flag for low docker storage and high docker memory usage
  (zhiwliu@redhat.com)
- Update lib_openshift to point to the stable 3.5 version (whearn@redhat.com)
- reverting back from ops carried iam modules (mwoodson@redhat.com)
- Adding defaults in case of puddle repos without ssl (kwoodson@redhat.com)
- Updating module to return arn. (kwoodson@redhat.com)
- Adding disk encryption and byo options. (kwoodson@redhat.com)
- first pass of updating meta/main.yml to point to the new upstream
  lib_openshift (whearn@redhat.com)
- put in a default for the us_private_ips (mwoodson@redhat.com)
- made generate byo have capability to do local ip addresses
  (mwoodson@redhat.com)
- Adding multi-inventory reboot cron to fix missing inventory.
  (kwoodson@redhat.com)
- Don't fail in openshift_dedicated_scripts but just print a message with the
  error (whearn@redhat.com)
- changed failed pv alerts only page on primary master (zhiwliu@redhat.com)
- Bypassing preflight checks. (kwoodson@redhat.com)
- back iops alert down to average, it's too flappy and generates false alerts
  as is (sten@redhat.com)
- missed disc. (sten@redhat.com)
- missing function name (sten@redhat.com)
- changed project operation check severity from high to avg
  (zhiwliu@redhat.com)
- change sop link (sten@redhat.com)
- Avoid use of globals in UDP limits role (joesmith@redhat.com)
- items don't exist at the moment, causing broken zabbix config loop
  (dranders@redhat.com)
- metrics every 30m, 2 fails in a row to trigger (dranders@redhat.com)
- add iops trigger (sten@redhat.com)
- Fix DNS whitelist destination, clean up node name (joesmith@redhat.com)
- added router2 key (zhiwliu@redhat.com)
- modify the sop for the project operation check (zhiwliu@redhat.com)
- added cron job for /usr/bin/cron-send-project-operation (zhiwliu@redhat.com)
- fixed epel yum exclude dependency (mwoodson@redhat.com)
- Touch SSO container's reconfig touchfile via ansible (joesmith@redhat.com)
- Add module for managing the "exclude" line of a yum repo config
  (joesmith@redhat.com)
- added the skip_if_unavailable option to our epel repo (mwoodson@redhat.com)
- cron changes based on arch meeting discussions (ihorvath@redhat.com)
- catching when OPENSHIFT-OUTPUT-FILTERING does not yet exist during
  provisioning (dedgar@redhat.com)
- catching when OPENSHIFT-OUTPUT-FILTERING does not yet exist during
  provisioning (dedgar@redhat.com)
- Re-add mistakenly-removed section to openshift_outbound_tcp_logging
  (joesmith@redhat.com)
- moving FORWARD logic to OPENSHIFT-OUTBOUND-FILTERING (dedgar@redhat.com)
- adding udp limit role with OPENSHIFT-OUTBOUND-FILTERING support
  (dedgar@redhat.com)
- Put forward_chain_bandaid.py cron job in correct location
  (joesmith@redhat.com)
- Add cron job to run forward_chain_bandaid.py every minute
  (joesmith@redhat.com)
- upped the host monitoring service timeout to 10 minutes (mwoodson@redhat.com)
- update all links to ops-sop (blentz@redhat.com)
- fixed oc_Version to have results instead of result. This is upstream
  compatible now (mwoodson@redhat.com)
- removed the debug for deploying the zagg service (mwoodson@redhat.com)
- add zabbix key for cron-send-project-operation.py (zhiwliu@redhat.com)
- Filter out JenkinsPipelines from stuck builds check (bmorriso@redhat.com)
- lowering alert to avg (mmahut@redhat.com)
- Add ability to exclude pkgs from EPEL repos (joesmith@redhat.com)
- zabbix: removed config loop client data from the config loop template
  (already in config loop client template) (mwoodson@redhat.com)
- fix a typo (zhizhang@zhizhang-laptop-nay.redhat.com)
- add cronjob and trigger for dnsmasq (zhizhang@zhizhang-laptop-nay.redhat.com)
- updated the ovs check to fire if not 2 or 4 nodes are there
  (mwoodson@redhat.com)
- add some defaults for httptests (jdiaz@redhat.com)
- Install correct openshift-dedicated-scripts versios. (dgoodwin@redhat.com)
- Fix zabbix config loop problems. (twiest@redhat.com)
- Change the zabbix history from the default of 90 days to a default of 14
  days. (twiest@redhat.com)
- Revert "Changed base OS level checks to run every minute so that Jeremy
  Eder's team can use our zabbix data." (twiest@redhat.com)
- correcting description (dranders@redhat.com)
- webcheck for developer.redhat.com sso (dranders@redhat.com)
- Changed the priority of the 'ebs volume stuck in transition state' check from
  average to high. (twiest@redhat.com)
- Reduced the amount of time that a router dynamic item macro stays around.
  (twiest@redhat.com)
- Added host monitoring cron job for cron-send-ec2-ebs-volumes-in-stuck-state.
  (twiest@redhat.com)
- Added cron-send-ec2-ebs-volumes-in-stuck-state.py (twiest@redhat.com)
- as per bign, we are doing rslave every cluster and no more /var/lib/docker
  mounting (ihorvath@redhat.com)
- zabbix webchecks for v3 SSO (dranders@redhat.com)
- adding default for v2_url, so local dev works (ihorvath@redhat.com)
- allow dig ansible lookups (jdiaz@redhat.com)
- ansible suggests this is how we should run on one host only with serial
  (ihorvath@redhat.com)
- allow overriding the way / ismounted (jdiaz@redhat.com)
- don't restart service if it's disabled (jdiaz@redhat.com)
- fix description of rss alert (zhizhang@zhizhang-laptop-nay.redhat.com)
- add check for dnsmasq (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix typo for memory_rss (zhizhang@zhizhang-laptop-nay.redhat.com)
- Added container usage regexes for zabbix and ops registry pods.
  (twiest@redhat.com)
- fix the value trans for the G (zhizhang@zhizhang-laptop-nay.redhat.com)
- add sop for the alert (zhizhang@zhizhang-laptop-nay.redhat.com)
- add alert for docker usage (zhizhang@zhizhang-laptop-nay.redhat.com)
- change metrics check alert from average to high (zhizhang@zhizhang-laptop-
  nay.redhat.com)
- added some debug to the zagg deployer (mwoodson@redhat.com)
- fixed the template deployer role (mwoodson@redhat.com)
- Add new role binding for logging for 3.4 (whearn@redhat.com)
- changing template and run file to get local dev working with 1.4
  (ihorvath@redhat.com)
- added the aws pre warm role (mwoodson@redhat.com)
- Increasing timeout after restart (jupierce@redhat.com)
- add openjdk rpm for systems that we initiate installations from
  (jdiaz@redhat.com)
- add cron job that cycles router pods if a cluster requires this
  (jdiaz@redhat.com)
- added httpd-tools to the os_utils to get installed during image creating and
  bootstrap (mwoodson@redhat.com)
- Lowering metrics alert severity to average (bmorriso@redhat.com)
- Improve documentation on iptables_chain module (joesmith@redhat.com)
- Add lib_ops_utils roles & iptables_chain module (joesmith@redhat.com)
- Restart Apache httpd if secrets change (joesmith@redhat.com)
- Don't restart SSO pods on secrets change (joesmith@redhat.com)
- check for pruning flag (sten@redhat.com)
- Vendoring openshift-ansible 3.6 (jupierce@redhat.com)
- updated the byo for rencrypt on the registry (mwoodson@redhat.com)
- Added fix for contiv role to the vendoring openshift-ansible role.
  (twiest@redhat.com)
- log pruning output to a file in the container (sten@redhat.com)

* Thu Apr 06 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.38-1
- Raising heartbeat frequency for synthetic hosts to every minute
  (bmorriso@redhat.com)
- Returning hosts from a hostgroup. (kwoodson@redhat.com)
- Adding debug for zbx get_host_ids error (jupierce@redhat.com)
- added support for lib_vendored_deps (mwoodson@redhat.com)
- updated the byo generate to have options passed in for logging and metrics
  (mwoodson@redhat.com)
- made the obg_registry need to pass in (mwoodson@redhat.com)
- Reverting changes to ha_proxy setup (jupierce@redhat.com)
- updated the logging to retry more for creating the project
  (mwoodson@redhat.com)
- added sdn and service network options to gen byo (mwoodson@redhat.com)
- more changes for gen_byo (mwoodson@redhat.com)
- Tested idempotency and removed now un-necessary delete section
  (chmurphy@redhat.com)
- Use new oc_configmap to pay back tech debt (chmurphy@redhat.com)
- Use oc_volume to add the router configmap volume. (bbarcaro@redhat.com)
- updated the generate byo to support router, reg, logging, metrics
  (mwoodson@redhat.com)
- Fixed 3.4 output for list-pods. (kwoodson@redhat.com)
- add new mothed to get pv usage in new version of openshift (zhizhang
  @zhizhang-laptop-nay.redhat.com)
- add checks for docker usage of rss and vms (zhizhang@zhizhang-laptop-
  nay.redhat.com)
- adding conditionals (dedgar@redhat.com)
- Fix fluentd on 3.4 installs (whearn@redhat.com)
- adjusting trigger names (mmahut@redhat.com)
- Send the quick heartbeat data every minute (mmahut@redhat.com)
- Changing the paging for heartbeat to 5/15 minutes (avg/high)
  (mmahut@redhat.com)
- making more comment revisions (dedgar@redhat.com)
- making more comment revisions (dedgar@redhat.com)
- Configure the OpenShift Online haproxy (chmurphy@redhat.com)
- fixed an issue  with the openshift default ns settings role
  (mwoodson@redhat.com)
- making comment revisions (dedgar@redhat.com)
- logging container outbound TCP connections (dedgar@redhat.com)
- Increase metrics deployer wait to 15 minutes. (dgoodwin@redhat.com)
- Changing critical memory level alert to average (mwhittingham@redhat.com)
- fixed naming issue for storageclass (mwoodson@redhat.com)
- Adding 'openshift_template_deployer' role (jupierce@redhat.com)
- Start specifying v3.4 for the metrics image version. (dgoodwin@redhat.com)
- Fix for empty string getting converted to None and treated as None.
  (kwoodson@redhat.com)
- Adding interface to call lib_openshift group/user policy module
  (jupierce@redhat.com)
- Mount the entire host FS on the host monitoring container's /host
  (joesmith@redhat.com)
- updated the subdomain variable in the byo generator (mwoodson@redhat.com)
- Pass in logging image version (whearn@redhat.com)
- Add view role to hawkular SA before launching metrics deployer.
  (dgoodwin@redhat.com)
- Lower the critical memory alert to avg (mmahut@redhat.com)
- Add check to see if Zabbix is running the most recent LTS version
  (joesmith@redhat.com)
- cleaned up logic in gcloud label, fixed a zone issue (mwoodson@redhat.com)
- cleaned up project in various gcloud modules (mwoodson@redhat.com)
- cleaned up gcloud_compute_label (mwoodson@redhat.com)
- re-did the lib_gcloud compute_labels to have pythonic input
  (mwoodson@redhat.com)
- added lib_gcloud gcloud_compute_label (mwoodson@redhat.com)
- updated the config loop enabled checks with sop (mwoodson@redhat.com)
- updated the timings (mwoodson@redhat.com)
- fixed the config loop client triggers (mwoodson@redhat.com)
- enabled the checks for the host monitoring to check the config loop tags
  (mwoodson@redhat.com)
- added the config loop client (mwoodson@redhat.com)
- added the zabbix config loop client template (mwoodson@redhat.com)
- fixed dumb typo in zabbix config loop (mwoodson@redhat.com)
- added triggers for config loop monitoring (mwoodson@redhat.com)
- config loop tag monitoring work (mwoodson@redhat.com)
- don't apply PROXY env var changes to 3.3 clusters (jdiaz@redhat.com)
- Adding python-manageiq-client to tower (bmorriso@redhat.com)
-  Updating playbook for setting up hawkular provider in miq
  (bmorriso@redhat.com)
- update monitoring-config.yml.j2 without hour specification
  (zhiwliu@redhat.com)
- add cronjob for internal-pods-check (zhiwliu@redhat.com)
- updated oo_ami copy to have new sa-east-1 region (mwoodson@redhat.com)
- Rename version metrics with zabbix compatible prefix (zgalor@redhat.com)
- Add zabbix keys for rpm versions (zgalor@redhat.com)
- Add job that reports docker oc rpm versions daily (zgalor@redhat.com)
- change the Failed pv from info to high (zhizhang@zhizhang-laptop-
  nay.redhat.com)
- new MetricSender/ZaggSender uses metric_sender.yaml for config info
  (jdiaz@redhat.com)
- Enable cron-send-security-updates-count cron job (joesmith@redhat.com)
- host-monitoring: Have docker mount needed paths for hostpkg checks
  (joesmith@redhat.com)
- fixing up openshift_master_facts symlink in the vendor issues
  (mwoodson@redhat.com)
- added the vendor_openshift_ansible_rpms tools role; update the vendor rpm to
  use it (mwoodson@redhat.com)
- Add cron-send-security-updates-count (joesmith@redhat.com)
- add openshift.master.pv.bound.count to cluster count graph (jdiaz@redhat.com)
- raise exceptions when walking through object path (jdiaz@redhat.com)

* Wed Feb 22 2017 Dan Yocum <dyocum@redhat.com> 0.0.37-1
- Properly wait for metrics deploy to complete. (dgoodwin@redhat.com)
- add key for internal pods check (zhiwliu@redhat.com)
- fixed type chioces -> choices (dyocum@redhat.com)
- use replace to do in-place updates when there are router changes
  (jdiaz@redhat.com)
- router DC changes for setting x_forwarded_for header (jdiaz@redhat.com)

* Mon Feb 20 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.36-1
- Add a git fetch module. (dgoodwin@redhat.com)
- Updated metrics playbook (sedgar@redhat.com)
- local development with 'oc cluster up' (jdiaz@redhat.com)
- remove ruamel.yaml in favor of python2-ruamel-yaml (mwoodson@redhat.com)
- changed to the new python2-ruamel-yaml file (mwoodson@redhat.com)
- added us-east-2 as a region to copy ami's to (mwoodson@redhat.com)
- add the brackets for monitoring-config.yml.j2 (zhiwliu@redhat.com)
- changed cron-send-elb-status just for aws cluster (zhiwliu@redhat.com)
- added a check for the serial cert file in the registry setup
  (mwoodson@redhat.com)
- changed volume provisioner to use openshift-scripts-dedicated
  (mwoodson@redhat.com)
- Enhancements to registery and route for 3.5 (kwoodson@redhat.com)
- defaultMode field on secret causing oadm_router to detect changes when there
  were none (jdiaz@redhat.com)
- add cronjob for the pvusage (zhizhang@zhizhang-laptop-nay.redhat.com)
- Added miq-setup.yml (twiest@redhat.com)
- typo fix in protocAls, and 3.4 fixes for smooth operation
  (ihorvath@redhat.com)
- upped the timeouts for logging/metrics (mwoodson@redhat.com)
- add applications as string to zhttptests (sten@redhat.com)
- add applications as string to zhttptests (sten@redhat.com)
- test adding application to web check (sten@redhat.com)
- Add OpenShift master audit config role. (dgoodwin@redhat.com)

* Tue Jan 31 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.35-1
- extra word in build_state.new key (sten@redhat.com)
- Fix docker oc version script (zgalor@redhat.com)
- monitor v2 zabbix ui from v3 zabbix server (sten@redhat.com)
- fix --api-ping param typo (jdiaz@redhat.com)
- made it possible to pass in default dm basesize for docker storage setup
  (mwoodson@redhat.com)
- Removing the available PV trigger (mmahut@redhat.com)
- move the node check to the primary master (zhizhang@zhizhang-laptop-
  nay.redhat.com)
- disable cron job that checks dns on existing containers (jdiaz@redhat.com)
- get logging and metrics working on 3.4 (mwoodson@redhat.com)
- Adding openshift sysctl role (kwoodson@redhat.com)
- added the storage class role, updated oc_label (mwoodson@redhat.com)
- Fixing zbx_action to filter instead of wildcard search (kwoodson@redhat.com)
- debug run time of oc commands, line up in-script timeouts so ops-runner
  timeout is less likely to fire (sten@redhat.com)

* Thu Jan 19 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.34-1
- Updating SOP URL and adding script to spec file (bmorriso@redhat.com)
- Updated script and cronjob to work with any build state.
  (bmorriso@redhat.com)
- Adding stuck build check, cronjob, zitem, ztrigger (bmorriso@redhat.com)
- updated oc_obj (mwoodson@redhat.com)
- add checks for pv usage (zhizhang@zhizhang-laptop-nay.redhat.com)
- role for deploying zagg in cluster (ihorvath@redhat.com)
- Change Ansible inventory and docker start to use ops-metric-client instead of
  zagg (zgalor@redhat.com)
- use correct name to script (and update ops-runner signature)
  (jdiaz@redhat.com)
- use logging ca in route to avoid 503 errors (sedgar@redhat.com)
- remove route until we can determine what is causing 503 error
  (sedgar@redhat.com)
- Update hawkular limits (whearn@redhat.com)
- use ops-metric-pcp-client instead of ops-zagg-pcp-client (jdiaz@redhat.com)
- use ops-metric-client instead of ops-zagg-client (jdiaz@redhat.com)
- add default image prefix (sedgar@redhat.com)
- add variable for image prefix (sedgar@redhat.com)
- Use universal read mode when opening cert files. (sedgar@redhat.com)
- add reencrypt route to logging (sedgar@redhat.com)
- use ops registry for logging images (sedgar@redhat.com)
- changed key names, added key for unknown state (sten@redhat.com)
- remove old zabbix config section (now metric_sender_config)
  (jdiaz@redhat.com)
- add nodata trigger for config loop (dranders@redhat.com)
- run cron-send-build-counts under ops-monitor (sten@redhat.com)
- remove unused kubeconfig check (jdiaz@redhat.com)
- add build count script, cronjob, zitem, ztrigger (sten@redhat.com)

* Wed Jan 04 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.33-1
- rename openshift-tools-scripts-monitoring-zagg-client (jdiaz@redhat.com)
- Openshift Installer no longer supports 'online' deployment type
  (mwoodson@redhat.com)
- Adding cron-send-elb-status.py to monitoring (mmahut@redhat.com)
- AMI prep role. (kwoodson@redhat.com)
- added ca-central-1 (mwoodson@redhat.com)
- Don't use oc import-image. It breaks some tags. (sedgar@redhat.com)
- Remove sorting as it breaks order of arrays. (kwoodson@redhat.com)
- Undo addition of broken parameter to SSO monitoring (joesmith@redhat.com)
- Fixing the wrapper that reports inventory to zabbix. (kwoodson@redhat.com)
- oc_image module implements image-import (ihorvath@redhat.com)

* Tue Dec 13 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.32-1
- Skip accounts that do not have creds. (kwoodson@redhat.com)
- add missing url field (jdiaz@redhat.com)
- preserve yaml formatting in monitoring-config.yml (jdiaz@redhat.com)
- Generate metric_sender.yaml from template (zgalor@redhat.com)
- Revert "made the lib_iam_accountid support aws_profiles"
  (mwoodson@redhat.com)
- Fix sso group sum aggregate item, add to Ops SSO App (joesmith@redhat.com)
- Adding multi-inventory template to ansible-tower hosts. (kwoodson@redhat.com)
- Adding inventory check to zabbix. (kwoodson@redhat.com)
- made the lib_iam_accountid support aws_profiles (mwoodson@redhat.com)
- Moving from iam to sts query for account and name. (kwoodson@redhat.com)
- Moving from iam to sts query for account and name. (kwoodson@redhat.com)
- added some variables to host_monitoring to allow for running or not
  (mwoodson@redhat.com)
- Fixing a variable bug. (kwoodson@redhat.com)
- Adding log file and setting permissions. (kwoodson@redhat.com)
- Adding new user ops_monitoring (mmahut@redhat.com)

* Thu Dec 08 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.31-1
- Skipping error'd accounts.  Instead of raising an exception, print to stderr.
  (kwoodson@redhat.com)
- Fixed when attribute does not exist. (kwoodson@redhat.com)
- Keeping block style on default creates. (kwoodson@redhat.com)
- removed the oc header (mwoodson@redhat.com)
- adding sso checks to zabbix (dedgar@redhat.com)
- Updated location for logging-deployer.yaml (whearn@redhat.com)
- Add a wait around the elasticsearch redeploy (whearn@redhat.com)
- Redeploy ES after attaching PV (whearn@redhat.com)
- Revert "determine path based on kube version" (sedgar@redhat.com)
- determine path based on kube version (sedgar@redhat.com)
- Fix metrics route and image settings (sedgar@redhat.com)
- more git automation work (mwoodson@redhat.com)
- adding sso checks to zabbix (dedgar@redhat.com)
- Updated location for logging-deployer.yaml (whearn@redhat.com)
- Add a wait around the elasticsearch redeploy (whearn@redhat.com)
- Redeploy ES after attaching PV (whearn@redhat.com)
- Add authorized_keys file for SSO monitoring container (joesmith@redhat.com)
- Upping the limits for hawkular (whearn@redhat.com)
- Run heartbeater in sso monitoring to create zabbix items
  (joesmith@redhat.com)
- Ami copy to module (kwoodson@redhat.com)
- updated repoquery for bug fix; updated epel_repository (mwoodson@redhat.com)
- Add secrets for zagg and generate zagg config (joesmith@redhat.com)
- Moving to ruamel yaml for preserving comments (kwoodson@redhat.com)
- add role to move PVs from one AZ to another (jdiaz@redhat.com)
- Add monitoring container to SSO app template (joesmith@redhat.com)
- Move generated "secrets" to emptydir volume in SSO app (joesmith@redhat.com)
- Fix improperly formated keys in multi_inventory (rharriso@redhat.com)
- Add OO_PAUSE_ON_{START,BUILD} placeholders for SSO apps (joesmith@redhat.com)
- updated the aws elb instance tries (mwoodson@redhat.com)
- Add a pause to allow curator edits to finish before redeploying
  (rharriso@redhat.com)
- Add authorized_keys file for SSO monitoring container (joesmith@redhat.com)
- Upping the limits for hawkular (whearn@redhat.com)
- Run heartbeater in sso monitoring to create zabbix items
  (joesmith@redhat.com)
- Ami copy to module (kwoodson@redhat.com)
- updated repoquery for bug fix; updated epel_repository (mwoodson@redhat.com)
- Add secrets for zagg and generate zagg config (joesmith@redhat.com)
- Moving to ruamel yaml for preserving comments (kwoodson@redhat.com)
- Revert "determine path based on kube version" (sedgar@redhat.com)
- add role to move PVs from one AZ to another (jdiaz@redhat.com)
- determine path based on kube version (sedgar@redhat.com)
- Fix metrics route and image settings (sedgar@redhat.com)
- Add monitoring container to SSO app template (joesmith@redhat.com)
- Move generated "secrets" to emptydir volume in SSO app (joesmith@redhat.com)
- Fix improperly formated keys in multi_inventory (rharriso@redhat.com)
- Add OO_PAUSE_ON_{START,BUILD} placeholders for SSO apps (joesmith@redhat.com)
- updated the git libraries to use ssh (mwoodson@redhat.com)
- more fixes for the git tools (mwoodson@redhat.com)
- updated the aws elb instance tries (mwoodson@redhat.com)
- Add support for monitoring secrets to openshift_sso_app (joesmith@redhat.com)
- Make a way to get file contents from aws_account_list role
  (joesmith@redhat.com)
- Fix openshift_sso_app markdown formatting in README (joesmith@redhat.com)
- wait rather than exit while the iptables lock is held (jdiaz@redhat.com)
- Move code for finding running pods from jinja to python filter plugin
  (joesmith@redhat.com)
- Add auto-deploy role for SSO app (joesmith@redhat.com)
- Add a pause to allow curator edits to finish before redeploying
  (rharriso@redhat.com)
- Fix default edit actions for router creation (rharriso@redhat.com)
- set ReclaimPolicy to Delete so controller will delete used volumes
  (sedgar@redhat.com)
- Ignore auto-generated values when comparing resources in oc_process
  (joesmith@redhat.com)
- Fix oc_process for reconcile runs. Add FIXME about possible logic error
  (joesmith@redhat.com)
- Allow openshift_cmd to take input to pipe to oc's stdin (joesmith@redhat.com)
- Wait for kibana to finish (whearn@redhat.com)
- make sure latest openshift-ansible-roles is installed (mwoodson@redhat.com)
- updated logging project description (mwoodson@redhat.com)
- add support for a 'list' with --all-namespaces (jdiaz@redhat.com)
- Make sure bad SSL certs won't break the routers (rharriso@redhat.com)
- Added limits around router and registry (whearn@redhat.com)
- Fix ansible_tower role item not compatible with new Ansible
  (joesmith@redhat.com)
- Adding apache license. (kwoodson@redhat.com)
- * logger.critical on timeout * section heading comments * magic variables
  bought to top * write logs to file for further review, only show last 20
  lines * add basename to differentiate between processes * noPodCount should
  be active even if there's been a pod found (dranders@redhat.com)
- Fix required variable quoting for Ansible 2.2 (rharriso@redhat.com)
- add cluster-wide router stats reporting cron job (jdiaz@redhat.com)
- Add openshift_aws_iam_sso role to manage IAM configuration of SAML IdP
  (joesmith@redhat.com)
- Adding region to host monitoring container (kwoodson@redhat.com)
- app create v2 command line arguments (dranders@redhat.com)
- Adding start_date. (kwoodson@redhat.com)
- logging syntax fix (whearn@redhat.com)
- description fix for logging project (whearn@redhat.com)
- Add new line at the end of openshift_metrics/defaults/main.yml
  (whearn@redhat.com)
- Minor formatting changes (whearn@redhat.com)
- Add constraints around hawkular and heapster (whearn@redhat.com)

* Tue Nov 08 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.30-1
- Fix for zabbix maintenance. (kwoodson@redhat.com)
- changed the package cleanup option (mwoodson@redhat.com)
- Update logging installer (whearn@redhat.com)
- fixed some output of package_update_needed (mwoodson@redhat.com)
- router monitoring (jdiaz@redhat.com)
- Fixing a bug with the yedit separator and _replace_content.
  (kwoodson@redhat.com)
- lets update docker, for now (mwoodson@redhat.com)
- added the openshift_update_packages role (mwoodson@redhat.com)
- Modifying yum_repos to use yum_repository call. (kwoodson@redhat.com)
- add items to hold openshift router health status (jdiaz@redhat.com)
- change/add error handling on zabbix ansible module (jdiaz@redhat.com)
- fix up some metrics and logging trigger expressions (jdiaz@redhat.com)
- modify the /usr/bin/cron-send-docker-metrics path (zhiwliu@redhat.com)
- Fixing an incorrect msg variable. (kwoodson@redhat.com)
- Ansible 2.2 broke the parameter message.  Updating to msg.
  (kwoodson@redhat.com)
- Adding rc for retry loops. (kwoodson@redhat.com)
- added package_update_needed and os_update_latest (mwoodson@redhat.com)
- Idempotently add or remove repo ids. (kwoodson@redhat.com)
- fixed the user writing adding in gcp (mwoodson@redhat.com)
- updated the verfiy aws role (mwoodson@redhat.com)
- sadly cron is running without the right environmental vars
  (ihorvath@redhat.com)
- updated repoquery (mwoodson@redhat.com)

* Thu Oct 27 2016 Ivan Horvath <ihorvath@redhat.com> 0.0.29-1
- aws_account_list: Pass in path to aws_accounts.txt (joesmith@redhat.com)
- fix spelling error in multi_inventory (blentz@redhat.com)
- add synthetic property that ossh can use to filter out synth hosts.
  (blentz@redhat.com)
- don't use global variable in role (jdiaz@redhat.com)
- fixed the openshift_numeric (mwoodson@redhat.com)
- fixed a bug with pv vars (mwoodson@redhat.com)
- use current version of docker (mwoodson@redhat.com)
- moved nickhammond logrotate to logrotate (mwoodson@redhat.com)
- added nickhammond.logrotate (mwoodson@redhat.com)
- Bypass templates that are not idempotent. (kwoodson@redhat.com)
- fixing the call to the tagged image: (ihorvath@redhat.com)
- fixed oc version issue (mwoodson@redhat.com)
- fixed oc version issue with metrics (mwoodson@redhat.com)
- added playbook to detach failed PVs (sedgar@redhat.com)
- Set up resource constraints for metrics based on how many cassandra nodes we
  have (whearn@redhat.com)

* Tue Oct 25 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.28-1
- Updating awsutil to handle the refactor. (kwoodson@redhat.com)
- changing registry url to include environment for host monitoring pulls
  (ihorvath@redhat.com)
- change to 7d removal of data if not required, solve daily cert OK alerts
  (dranders@redhat.com)

* Mon Oct 24 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.27-1
- Fixed the library call for the multiinventory (kwoodson@redhat.com)

* Mon Oct 24 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.26-1
- Separating accounts. (kwoodson@redhat.com)
- updated git commit module (mwoodson@redhat.com)

* Mon Oct 24 2016 Wesley Hearn <whearn@redhat.com> 0.0.25-1
- reducing priority on config run, there is no reason for this to page
  (ihorvath@redhat.com)
- Fix around oo_zabbix role and logging (whearn@redhat.com)
- Attempt at making oc_process idempotent. (kwoodson@redhat.com)
- add support for setting up multiple OpenShift routers (jdiaz@redhat.com)
- Fix config for container usage to be compatible with ansible 2.x
  (twiest@redhat.com)
- Added quick and dirty disk check (whearn@redhat.com)
- remove ignore_errors (sedgar@redhat.com)
- fixed the registry options in oadm_registry (mwoodson@redhat.com)
- improve upgrade-check variables (sedgar@redhat.com)
- Adding statuspage component (kwoodson@redhat.com)
- set verbosity (dranders@redhat.com)
- generated namespace exceeds limit (dranders@redhat.com)
- Fixed description bug and added workaround for project/namespace issue.
  (kwoodson@redhat.com)
- Fixed a couple bugs found by the team (sedgar@redhat.com)
- pass the name when creating router template output (jdiaz@redhat.com)
- added kube version to the metrics; cleaned up template installer
  (mwoodson@redhat.com)
- added FIXME statements for future improvements (sedgar@redhat.com)
- Add logging vars file (whearn@redhat.com)
- Add logging checks (whearn@redhat.com)
- Add trigger to alert on metrics failing (whearn@redhat.com)
- updated oc version with a few cleanup steps (mwoodson@redhat.com)
- added playbook for in-place rpm hotfixes (sedgar@redhat.com)
- added lib_repoquery (mwoodson@redhat.com)
- Adding statuspage ansible module. (kwoodson@redhat.com)
- seperate the builds (dranders@redhat.com)
- Add metrics check cronjob (whearn@redhat.com)
- updated the git_commit to have better logic (mwoodson@redhat.com)
- added git_commit module to take files to commit argument
  (mwoodson@redhat.com)
- add Terminating project check (zhizhang@redhat.com)

* Thu Oct 13 2016 Wesley Hearn <whearn@redhat.com> 0.0.24-1
- Add host template to primary masters (whearn@redhat.com)
- Fix zabbix key names (whearn@redhat.com)
- Few bug fixes around metrics (whearn@redhat.com)
- Create metrics template (whearn@redhat.com)

* Wed Oct 12 2016 Wesley Hearn <whearn@redhat.com> 0.0.23-1
- extension was missing from include_vars file (ihorvath@redhat.com)
- Add legacy V2 AWS accounts to parsable list of AWS accounts
  (joesmith@redhat.com)
- Fix aws user role to work with Ansible 2.2 (joesmith@redhat.com)
- Add openshift metrics checks. Updated ocutil with more features
  (whearn@redhat.com)
- from discussion with devs we are increasing the threshold of etcd connection
  trigger (ihorvath@redhat.com)
- Deadlock fix in git module. (kwoodson@redhat.com)
- disable router and registry in the byo installer (mwoodson@redhat.com)
- added some fixes for the upgrade steps (mwoodson@redhat.com)
- added the openshift_aws_elb instance manager role (mwoodson@redhat.com)
- append to log instead of overwriting (sedgar@redhat.com)
- run every 10 minutes (sedgar@redhat.com)
- Added role to generate byo inventory files (whearn@redhat.com)
- ugrade fixes (mwoodson@redhat.com)
- save log output, exclude openshift project, use grep instead of diff
  (sedgar@redhat.com)
- append now creates array when it does not exist. (kwoodson@redhat.com)
- added cron script to delete stuck projects for bz 1367432 (sedgar@redhat.com)
- Force options added to evacuate. (kwoodson@redhat.com)
- Updated manage node to support empty pod lists. Idempotent schedulable
  (kwoodson@redhat.com)
- changing file lock mutex (dranders@redhat.com)
- Updating to handle the 3.2 to 3.3 upgrade path. (kwoodson@redhat.com)
- made playbook work with Online nodes (sedgar@redhat.com)
- updated oc_version (mwoodson@redhat.com)
- Removing wait in favor of communicate to avoid deadlock.
  (kwoodson@redhat.com)
- updated git libs (mwoodson@redhat.com)
- Add cluster capacity alerts in Zabbix (rharriso@redhat.com)
- Pass in cafile to openshift_hosted_router_certificate (whearn@redhat.com)
- Removed extra ' (whearn@redhat.com)
- Generate easily parsable list of AWS accounts (joesmith@redhat.com)
- increasing threshold numbers per discussion with twiest (ihorvath@redhat.com)
- Add missing ' (whearn@redhat.com)
- Make new nodes with schedulable set to false (whearn@redhat.com)
- Scale registry to infra node count. (kwoodson@redhat.com)
- Removing the delete with the latest iam_cert20 module update.
  (kwoodson@redhat.com)
- update cron job that launches event watcher (jdiaz@redhat.com)
- Added role to generate byo inventory files (whearn@redhat.com)
- Fixed a missing comma. (kwoodson@redhat.com)
- Fixing router with latest edit code.  Updated yedit to handle content.
  (kwoodson@redhat.com)
- Attempting to fix NoneType in edits. (kwoodson@redhat.com)
- When there are no edits then default to empty dict. (kwoodson@redhat.com)
- update event watcher with regex ability (jdiaz@redhat.com)
- Fixing yedit for 2.2 with content_type: str (kwoodson@redhat.com)
- oc_version (kwoodson@redhat.com)
- Work around omit not working for dictionaries (rharriso@redhat.com)
- Add second cassandra node to deployments (rharriso@redhat.com)
- Fixing return value for ansible 2.2. (kwoodson@redhat.com)
- Cleaning up from yedit move to periods. (kwoodson@redhat.com)
- Latest yedit added and generated. (kwoodson@redhat.com)
- Yedit changed to handle periods.  Moving to periods as default separator.
  (kwoodson@redhat.com)
- Allow different separators. (kwoodson@redhat.com)

* Mon Sep 26 2016 Ivan Horvath <ihorvath@redhat.com> 0.0.22-1
- Adding oadm_manage_node. (kwoodson@redhat.com)
- Adding ability to perform router edits at creation time.
  (kwoodson@redhat.com)

* Thu Sep 22 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.21-1
- wrap inventory refresh in ops-runner (to post result to zabbix)
  (jdiaz@redhat.com)
- fixed a debug msg for ansible 2.2 (mwoodson@redhat.com)
- cleaned up registry cert role (mwoodson@redhat.com)

* Thu Sep 22 2016 Joel Diaz <jdiaz@redhat.com> 0.0.20-1
- shuffle files around to make local development easier (jdiaz@redhat.com)

* Tue Sep 20 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.19-1
- Added gcs monitoring. (kwoodson@redhat.com)
- Adding zabbix objects for gcp snapshotting. (kwoodson@redhat.com)
- fixing aws user role for ansible 2 (mwoodson@redhat.com)

* Fri Sep 16 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.18-1
- Fixes for labeling, snapshotting, and trimming snapshots.
  (kwoodson@redhat.com)

* Thu Sep 15 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.17-1
- fixed monitoring template (mwoodson@redhat.com)

* Thu Sep 15 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.16-1
- Fixing code for snapshots. (kwoodson@redhat.com)
- First attempt at zabbix maintenance. (kwoodson@redhat.com)
- fix a the name typo (zhizhang@zhizhang-laptop-nay.redhat.com)
- fixed debug to use a msg instead of var (mwoodson@redhat.com)
- First attempt at maintenance (kwoodson@redhat.com)
- updated some code docs (mwoodson@redhat.com)
- updated oc_label to handle selectors and multiple labels at a time
  (mwoodson@redhat.com)
- First attempt at zabbix maintenance. (kwoodson@redhat.com)
- fix a the name typo (zhizhang@zhizhang-laptop-nay.redhat.com)
- router doens't support edits yet (mwoodson@redhat.com)
- made edits to router/registry to use registry.ops (mwoodson@redhat.com)
- added config changes to registry deployer (mwoodson@redhat.com)
- fixed debug to use a msg instead of var (mwoodson@redhat.com)
- check for certs in /etc/origin/{master,node} (jdiaz@redhat.com)
- raise severity on config loop trigger to high (jdiaz@redhat.com)
- First attempt at maintenance (kwoodson@redhat.com)

* Mon Sep 12 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.15-1
- Fixing boolean strings for ansible 2.2 (kwoodson@redhat.com)
- ansible 2.2 task naming (jdiaz@redhat.com)
- Fix broken root session logrotate (joesmith@redhat.com)
- Updating from yedit to tools. (kwoodson@redhat.com)
- Adding documentation. (kwoodson@redhat.com)
- Added cgrouputil.py and changed dockerutil to be able to use it if requested.
  (twiest@redhat.com)
- Updating for 2.2. (kwoodson@redhat.com)
- changed kibana -> logs (mwoodson@redhat.com)
- Adding zabbix bits. (kwoodson@redhat.com)
- ansible 2.2 changes. (kwoodson@redhat.com)
- Fixed var name. (kwoodson@redhat.com)
- Adding types to config passed.  This caused an error in 2.2 so I'm explicitly
  setting them. (kwoodson@redhat.com)
- add steps to allow a clean system to ansible_tower role successfully
  (jdiaz@redhat.com)
- add firewalld rpm (jdiaz@redhat.com)
- no bare variables (jdiaz@use-tower2.ops.rhcloud.com)
- add Terminating project check (zhizhang@zhizhang-laptop-nay.redhat.com)
- commented out the fluentd container usage config as it's causing issues on
  some boxes and it's not required. (twiest@redhat.com)
- Added configs for cron-send-docker-containers-usage (twiest@redhat.com)
- change link for existing DNS alerts (sten@redhat.com)

* Wed Aug 31 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.14-1
- add OpenShift Cluster(wide) templates/items/triggers (jdiaz@redhat.com)
- Incorporate changes from arch meeting (rharriso@redhat.com)
- Make sure the checks aleart after the same time now that their interval has
  been increased (rharriso@redhat.com)
- Changes from Ops arch meeting (rharriso@redhat.com)
- don't need dnsmasq checks more than every 15 minutes (rharriso@redhat.com)
- Increase the interval for Zabbix checks to save on both DB load and space
  (rharriso@redhat.com)
- Added specific labels to host types. (kwoodson@redhat.com)
- have primary master heartbeat for synthetic host (jdiaz@redhat.com)
- Added cron-send-docker-containers-usage.py (twiest@redhat.com)
- Adding disk labels to deployment manager (kwoodson@redhat.com)
- changed rc to inherit from dc (mwoodson@redhat.com)
- removed comments (mwoodson@redhat.com)
- more updates to oc scale (mwoodson@redhat.com)
- more fixes for the metrics, included the copy (mwoodson@redhat.com)
- added some options to openshift ansible tools, added mem constraints for
  metrics (mwoodson@redhat.com)
- Add history and trends parameters to the zbx_item and zbx_itemprototype
  modules (rharriso@redhat.com)
- Comments to explain changes in the trigger logic (rharriso@redhat.com)
- Adding in-memory updates. (kwoodson@redhat.com)
- add triggers for iminent certificate expirations (jdiaz@redhat.com)
- add daily cron to report on certificate expirations (jdiaz@redhat.com)
- Minor fix for bool str (kwoodson@redhat.com)
- bind all of /etc/origin into host-monitoring (so we can see certificates)
  (jdiaz@redhat.com)
- fixed spelling error in volume provisioner (mwoodson@redhat.com)
- add items to hold certificate expiration data (jdiaz@redhat.com)
- add trigger and item for saml check (zhizhang@zhizhang-laptop-nay.redhat.com)
- added the openshift_volume_provisioner role (mwoodson@redhat.com)
- added urls for remaining pv check (sten@redhat.com)
- pass in cluster-wide KMS key to generated docker config (jdiaz@redhat.com)
- Fixed boolean passing as strings (kwoodson@redhat.com)
- sleep for a moment before getting newly create KMS data (jdiaz@redhat.com)
- Prune haproxy processes more aggressively (agrimm@redhat.com)
- add saml check (zhizhang@zhizhang-laptop-nay.redhat.com)
- run haproxy script every 15 minutes (jdiaz@redhat.com)
- Changed role openshift_dedicated_admin to explicitly turn off non-primary
  master dedicated-admin-role services. Added oda_config param.
  (twiest@redhat.com)
- add haproxy pruner cron job to infra nodes (jdiaz@redhat.com)
- add item to hold number of haproxy processes found in CLOSE-WAIT state
  (jdiaz@redhat.com)
- Added oda_skip_projects to the openshift_dedicated_admin role.
  (twiest@redhat.com)
- changed zabbix key for build time to match key sent by script
  (sten@redhat.com)
- enable creating encrypted PVs (jdiaz@redhat.com)
- allow tagging resulting AMI (jdiaz@redhat.com)
- add role that can be called during cluster creation (jdiaz@redhat.com)
- added the role openshift_gcp_add_users_to_project (mwoodson@redhat.com)
- role doesn't take osaik_kms_directory parameter (jdiaz@redhat.com)
- add oo_ec2_ami_copy Ansible module (jdiaz@redhat.com)
- Updating the name of the role to be more clear as to what it does
  (mwhittingham@redhat.com)
- GCP support for osohm (kwoodson@redhat.com)
- Forgot an example in the README (mwhittingham@redhat.com)
- Being more explicit about the oadm location (mwhittingham@redhat.com)
- added gcloud config ansible module, created a role with it
  (mwoodson@redhat.com)
- Initial commit (mwhittingham@redhat.com)
- use renamed oo_ec2_ami20 module (jdiaz@redhat.com)
- rename OpenShift Ops roles to prefix with oo_ ...to indicate that this is our
  module (not something pulled/backported) iam_kms cat_fact sysconfig_fact
  (jdiaz@redhat.com)
- added dnsmasq_proxy and dnsmasq_proxy_file (mwoodson@redhat.com)
- Fixes for gcp registry (kwoodson@redhat.com)
- added gcp zone getter (mwoodson@redhat.com)
- Adding gcp_compute_zones (kwoodson@redhat.com)
- added support for generic service account in gcp (mwoodson@redhat.com)
- using common kms names for each cluster (jdiaz@redhat.com)
- deal with rename of ec2_vol20 library (jdiaz@redhat.com)
- Separating registries.  Removing bucket from storage bucket name.
  (kwoodson@redhat.com)
- Fixed a bug in variable name caused by refactor. (kwoodson@redhat.com)
- add role to create and save AWS IAM KMS key data (jdiaz@redhat.com)
- Fix creating the zabbix config template (rharriso@redhat.com)
- Fixed json output format. (kwoodson@redhat.com)
- add AWS IAM KMS ansible library for creating/querying KMS entries
  (jdiaz@redhat.com)
- Have the Zabbix config run in cron and report results to Zabbix
  (rharriso@redhat.com)
- Making openshift_registry work on gcp and aws. Fixed service account keys.
  Added scopes to vminstances. (kwoodson@redhat.com)
- fixed dependency name (mwoodson@redhat.com)
- added ops_os_firewall (mwoodson@redhat.com)
- added ops_os_firewall (mwoodson@redhat.com)
- added dirty_os_firewall (mwoodson@redhat.com)
- Added creating snapshot tag for autoprovisioned PVs to cron.
  (twiest@redhat.com)
- added gcp service account, update haproxy passthrough (mwoodson@redhat.com)
- removed include (mwoodson@redhat.com)
- Normalizing on oo vars (kwoodson@redhat.com)
- Adding storage buckets to dm (kwoodson@redhat.com)
- Adding ability to change from cname to A record. (kwoodson@redhat.com)
- temporary fix for the wrong file extension issue (ihorvath@redhat.com)
- fixing yml extension (ihorvath@redhat.com)
- changing the location of inital config for osohm container
  (ihorvath@redhat.com)
- add synthetic cluster-wide host support to ops-zagg-client (jdiaz@redhat.com)
- added ops-runner timeouts to create-app tests (sten@redhat.com)
- moving everything from dynamic keys to static zabbix items
  (ihorvath@redhat.com)
- Improved nodes_not_schedulable check Check avoids master nodes Reincluded
  zabbix trigger for check (bshpurke@redhat.com)
- added tags support for the dm builder in gcp (mwoodson@redhat.com)
- etcd metrics with dynamic items in zabbix (ihorvath@redhat.com)
- Added graph for openshift.master.cluster.max_mem_pods_schedulable
  (twiest@redhat.com)
- add --timeout to ops-runner and a dynamic item to hold these items
  (jdiaz@redhat.com)
- Added more items and graphs for online preview cluster. (twiest@redhat.com)
- Removed not scheduled check (benpack101@gmail.com)
- delte the cert before upload (zhizhang@zhizhang-laptop-nay.redhat.com)
- more gcp roles and changes (mwoodson@redhat.com)
- Adding pd pv support for gcp dm (kwoodson@redhat.com)
- Adding request path (kwoodson@redhat.com)
- Adding service-account keys and policy (kwoodson@redhat.com)
- Fixed typo with node related zabbix checks(node-not-ready/not-labeled) Added
  zabbix check for non-schedulable nodes Added proper sop links in zabbix
  (bshpurke@redhat.com)
- Added compute node cpu idle and memory available averages items and graphs to
  zabbix (twiest@redhat.com)
- handle one case of not being able to remove the docker vg (sten@redhat.com)
- fixed var name in gcp cluster creation (mwoodson@redhat.com)
- put docker version to 1.9.1 (mwoodson@redhat.com)
- updated gcp cluster creation with reconciler (mwoodson@redhat.com)
- First attempt at the dm reconciler (kwoodson@redhat.com)
- Change config loop failure to a high alert (agrimm@redhat.com)
- removed old role git_rebase_upstream (mwoodson@redhat.com)
- fixed readme files (mwoodson@redhat.com)
- added new roles for gcp (mwoodson@redhat.com)
- First attempt at service account (kwoodson@redhat.com)
- removed warning in temp git dir (mwoodson@redhat.com)
- Fix param swap (kwoodson@redhat.com)
- Updating to take into account colons in ssh key hosts (kwoodson@redhat.com)
- logic fix for ssh key comparison (kwoodson@redhat.com)
- ProjectInfo added for sshkey support (kwoodson@redhat.com)
- Added graphs for scheduled and oversubscribed. (twiest@redhat.com)
- run event watch to catch/report FailedScheduling events (jdiaz@redhat.com)
- have all masters report cluster stats (not just primary master)
  (jdiaz@redhat.com)
- gcloud manifest added (kwoodson@redhat.com)
- add more generous random sleeping for various cron jobs (jdiaz@redhat.com)
- Update the docs for oso_host_monitoring (rharriso@redhat.com)
- Fixed the executable path of gcloud (kwoodson@redhat.com)
- Install the gcloud package which has gcloud cli (kwoodson@redhat.com)
- Added gcloud_compute_image ansible module (kwoodson@redhat.com)
- Added cluster capacity items. (twiest@redhat.com)
- Adding provisioning flag for metadata (kwoodson@redhat.com)
- Updating openshift-tools to use our own pylintrc.  disabling too-many-lines
  (kwoodson@redhat.com)
- Add basic dnsmasq monitoring template and cron configuration
  (rharriso@redhat.com)
- use --node-checks instead of --nodes-checks (jdiaz@redhat.com)
- Added check for nodes without labels (bshpurke@redhat.com)
- First attempt at resource builder for gcp (kwoodson@redhat.com)
- ensuring /var/log/rootlog directories get created (dedgar@redhat.com)
- ironed out ansible style issues and ensured profile directory gets created
  (dedgar@redhat.com)
- cleaning up rootlog portion (dedgar@redhat.com)
- cleaning up formatting (dedgar@redhat.com)
- adding initial rootlog configuration (dedgar@redhat.com)

* Wed Jul 06 2016 Joel Smith <joesmith@redhat.com> 0.0.13-1
- page out when app builds fail >2hr or app creates fail >1hr (sten@redhat.com)
- Add ops_map_format filter to the ops_filters plugin (joesmith@redhat.com)
- Made some tweaks to our users_available calculations per dmcphers feedback.
  (twiest@redhat.com)
- added debug info for nodes not ready check (sten@redhat.com)
- added ops_customizations (mwoodson@redhat.com)
- adding cpu and memory per process monitoring (ihorvath@redhat.com)
- Added ozcs_clusterid to the name in the graphs in os_zabbix_cluster_stats
  (twiest@redhat.com)
- Fixed bug in os_zabbix_cluster_stats (twiest@redhat.com)
- Added graphs for mem.users_available and cpu.users_available.
  (twiest@redhat.com)
- report average cpu and memory allocations for compute nodes across the
  cluster (jdiaz@redhat.com)
- Added features to graph_item (twiest@redhat.com)
- Added check to ops-docker-storage-reinitialize.yml for when the docker_vg is
  being used by another device. (twiest@redhat.com)
- mark zabbix item as a "%%" unit (jdiaz@redhat.com)
- Fixed bug in os_zabbix_cluster_stats (twiest@redhat.com)
- allow passing in auto-logout value for zabbix users (jdiaz@redhat.com)
- deal with new groups being added to a user (jdiaz@redhat.com)
- Added os_zabbix_cluster_stats (twiest@redhat.com)
- Added ability to create items directly on a host to the zbx_item ansible
  module. (twiest@redhat.com)
- add item to hold FailedScheduling event counts (jdiaz@redhat.com)
- Fixed openshift.master.avg_running_pods_per_user (twiest@redhat.com)
- Added metrics for openshift master memory and cpu for the number of users
  using the system. (twiest@redhat.com)
- First attempt at gcloud deployment-manager deployments. (kwoodson@redhat.com)

* Thu Jun 23 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.12-1
- Adding filter plugins from openshift-ansible and moved to ops
  (kwoodson@redhat.com)
- Adding params for calculated items (kwoodson@redhat.com)

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

