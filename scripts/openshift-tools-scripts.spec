Summary:       OpenShift Tools Scripts
Name:          openshift-tools-scripts
Version:       0.0.135
Release:       1%{?dist}
License:       ASL 2.0
URL:           https://github.com/openshift/openshift-tools
Source0:       %{name}-%{version}.tar.gz
BuildArch:     noarch

%description
OpenShift Tools Scripts

%prep
%setup -q

%build

%install

# openshift-tools-scripts-monitoring install
mkdir -p %{buildroot}/usr/bin
cp -p monitoring/ops-zagg-client.py %{buildroot}/usr/bin/ops-zagg-client
cp -p monitoring/ops-hawk-client.py %{buildroot}/usr/bin/ops-hawk-client
cp -p monitoring/ops-zagg-pcp-client.py %{buildroot}/usr/bin/ops-zagg-pcp-client
cp -p monitoring/ops-zagg-metric-processor.py %{buildroot}/usr/bin/ops-zagg-metric-processor
cp -p monitoring/ops-zagg-heartbeat-processor.py %{buildroot}/usr/bin/ops-zagg-heartbeat-processor
cp -p monitoring/ops-zagg-heartbeater.py %{buildroot}/usr/bin/ops-zagg-heartbeater
cp -p monitoring/cron-send-process-count.sh %{buildroot}/usr/bin/cron-send-process-count
cp -p monitoring/cron-send-filesystem-metrics.py %{buildroot}/usr/bin/cron-send-filesystem-metrics
cp -p monitoring/cron-send-pcp-sampled-metrics.py %{buildroot}/usr/bin/cron-send-pcp-sampled-metrics
cp -p monitoring/ops-runner.py %{buildroot}/usr/bin/ops-runner
cp -p monitoring/cron-event-watcher.py %{buildroot}/usr/bin/cron-event-watcher
cp -p monitoring/cron-send-ovs-status.py %{buildroot}/usr/bin/cron-send-ovs-status
cp -p monitoring/cron-send-pcp-ping.sh %{buildroot}/usr/bin/cron-send-pcp-ping
cp -p monitoring/cron-send-etcd-status.py %{buildroot}/usr/bin/cron-send-etcd-status
cp -p monitoring/cron-send-disk-metrics.py %{buildroot}/usr/bin/cron-send-disk-metrics
cp -p monitoring/cron-send-network-metrics.py %{buildroot}/usr/bin/cron-send-network-metrics
cp -p monitoring/cron-send-s3-metrics.py %{buildroot}/usr/bin/cron-send-s3-metrics
cp -p monitoring/cron-send-os-master-metrics.py %{buildroot}/usr/bin/cron-send-os-master-metrics
cp -p monitoring/cron-send-docker-metrics.py %{buildroot}/usr/bin/cron-send-docker-metrics
cp -p monitoring/cron-send-docker-timer.py %{buildroot}/usr/bin/cron-send-docker-timer
cp -p monitoring/cron-send-docker-containers-usage.py %{buildroot}/usr/bin/cron-send-docker-containers-usage
cp -p monitoring/cron-send-docker-dns-resolution.py %{buildroot}/usr/bin/cron-send-docker-dns-resolution
cp -p monitoring/cron-send-docker-existing-dns-resolution.py %{buildroot}/usr/bin/cron-send-docker-existing-dns-resolution
cp -p monitoring/cron-send-registry-checks.py %{buildroot}/usr/bin/cron-send-registry-checks
cp -p monitoring/ops-zbx-event-processor.py %{buildroot}/usr/bin/ops-zbx-event-processor
cp -p monitoring/cron-send-os-skydns-checks.py %{buildroot}/usr/bin/cron-send-os-skydns-checks
cp -p monitoring/cron-send-os-dnsmasq-checks.py %{buildroot}/usr/bin/cron-send-os-dnsmasq-checks
cp -p monitoring/cron-fix-ovs-rules.py %{buildroot}/usr/bin/cron-fix-ovs-rules
cp -p monitoring/cron-send-create-app.py %{buildroot}/usr/bin/cron-send-create-app
cp -p monitoring/cron-send-project-stats.py %{buildroot}/usr/bin/cron-send-project-stats
cp -p monitoring/cron-openshift-pruner.py %{buildroot}/usr/bin/cron-openshift-pruner
cp -p remote-heal/remote-healer.py %{buildroot}/usr/bin/remote-healer
cp -p cloud/aws/ops-ec2-copy-ami-to-all-regions.py %{buildroot}/usr/bin/ops-ec2-copy-ami-to-all-regions
cp -p cloud/aws/ops-ec2-snapshot-ebs-volumes.py %{buildroot}/usr/bin/ops-ec2-snapshot-ebs-volumes
cp -p cloud/aws/ops-ec2-trim-ebs-snapshots.py %{buildroot}/usr/bin/ops-ec2-trim-ebs-snapshots
cp -p cloud/aws/ops-ec2-add-snapshot-tag-to-ebs-volumes.py %{buildroot}/usr/bin/ops-ec2-add-snapshot-tag-to-ebs-volumes
cp -p cloud/gcp/ops-gcp-add-snapshot-label-to-pd-volumes.py %{buildroot}/usr/bin/ops-gcp-add-snapshot-label-to-pd-volumes
cp -p cloud/gcp/ops-gcp-snapshot-pd-volumes.py %{buildroot}/usr/bin/ops-gcp-snapshot-pd-volumes
cp -p cloud/gcp/ops-gcp-trim-pd-snapshots.py %{buildroot}/usr/bin/ops-gcp-trim-pd-snapshots
cp -p monitoring/cron-send-cluster-capacity.py %{buildroot}/usr/bin/cron-send-cluster-capacity
cp -p monitoring/cron-send-connection-count.py %{buildroot}/usr/bin/cron-send-connection-count
cp -p monitoring/cron-send-cpu-mem-stats.py %{buildroot}/usr/bin/cron-send-cpu-mem-stats
cp -p monitoring/cron-haproxy-close-wait.py %{buildroot}/usr/bin/cron-haproxy-close-wait
cp -p monitoring/cron-send-saml-status.py %{buildroot}/usr/bin/cron-send-saml-status
cp -p monitoring/cron-certificate-expirations.py %{buildroot}/usr/bin/cron-certificate-expirations

mkdir -p %{buildroot}/etc/openshift_tools
cp -p monitoring/zagg_client.yaml.example %{buildroot}/etc/openshift_tools/zagg_client.yaml
cp -p monitoring/hawk_client.yaml.example %{buildroot}/etc/openshift_tools/hawk_client.yaml
cp -p monitoring/zagg_server.yaml.example %{buildroot}/etc/openshift_tools/zagg_server.yaml
cp -p remote-heal/remote_healer.conf.example %{buildroot}/etc/openshift_tools/remote_healer.conf

mkdir -p %{buildroot}/var/run/zagg/data

# openshift-tools-scripts-inventory-clients install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}/etc/bash_completion.d
mkdir -p %{buildroot}/etc/openshift_tools
cp -p inventory-clients/{ohi,opscp,opssh,oscp,ossh} %{buildroot}%{_bindir}
cp -p inventory-clients/ossh_bash_completion %{buildroot}/etc/bash_completion.d
cp -p inventory-clients/openshift_tools.conf.example %{buildroot}/etc/openshift_tools/openshift_tools.conf

# ----------------------------------------------------------------------------------
# openshift-tools-scripts-inventory-clients subpackage
# ----------------------------------------------------------------------------------
%package inventory-clients
Summary:       OpenShift Tools Inventory Clients
Requires:      python2,python-openshift-tools-inventory-clients
BuildArch:     noarch

%description inventory-clients
OpenShift Tools Clients for interacting with hosts/inventory

%files inventory-clients
%{_bindir}/ohi
%{_bindir}/opscp
%{_bindir}/opssh
%{_bindir}/oscp
%{_bindir}/ossh
/etc/bash_completion.d/*
%config(noreplace)/etc/openshift_tools/openshift_tools.conf

# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring-remoteheal subpackage
# ----------------------------------------------------------------------------------
%package monitoring-remoteheal
Summary:       OpenShift Tools Monitoring Remote Heal Scripts
Requires:      python2,openshift-tools-scripts-inventory-clients
BuildArch:     noarch

%description monitoring-remoteheal
OpenShift Tools Monitoring Remoteheal Scripts

%files monitoring-remoteheal
/usr/bin/remote-healer
%config(noreplace)/etc/openshift_tools/remote_healer.conf

# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring-autoheal subpackage
# ----------------------------------------------------------------------------------
%package monitoring-autoheal
Summary:       OpenShift Tools Monitoring Autoheal Scripts
Requires:      python2,python-openshift-tools-monitoring-zagg,openvswitch
BuildArch:     noarch

%description monitoring-autoheal
OpenShift Tools Monitoring Autoheal Scripts

%files monitoring-autoheal
/usr/bin/cron-fix-ovs-rules
/usr/bin/cron-haproxy-close-wait

# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring-pcp subpackage
# ----------------------------------------------------------------------------------
%package monitoring-pcp
Summary:       OpenShift Tools PCP Monitoring Scripts
Requires:      python2,openshift-tools-scripts-monitoring-zagg-client,python-openshift-tools-monitoring-zagg,python-openshift-tools-monitoring-pcp,python-docker-py
BuildRequires: python2-devel
BuildArch:     noarch

%description monitoring-pcp
OpenShift Tools PCP Monitoring Scripts

%files monitoring-pcp
/usr/bin/cron-send-filesystem-metrics
/usr/bin/cron-send-pcp-sampled-metrics
/usr/bin/cron-send-pcp-ping
/usr/bin/cron-send-disk-metrics
/usr/bin/cron-send-network-metrics
/usr/bin/ops-zagg-pcp-client


# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring-docker subpackage
# ----------------------------------------------------------------------------------
%package monitoring-docker
Summary:       OpenShift Tools Docker Monitoring Scripts
Requires:      python2,python-openshift-tools-monitoring-zagg,python-openshift-tools-monitoring-docker,python-docker-py
BuildRequires: python2-devel
BuildArch:     noarch

%description monitoring-docker
OpenShift Tools Docker Monitoring Scripts

%files monitoring-docker
/usr/bin/cron-send-docker-metrics
/usr/bin/cron-send-docker-timer
/usr/bin/cron-send-docker-containers-usage
/usr/bin/cron-send-docker-dns-resolution
/usr/bin/cron-send-docker-existing-dns-resolution


# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring-zagg-client subpackage
# ----------------------------------------------------------------------------------
%package monitoring-zagg-client
Summary:       OpenShift Tools Zagg Client Monitoring Scripts
Requires:      python2,python-openshift-tools-monitoring-zagg
BuildRequires: python2-devel
BuildArch:     noarch

%description monitoring-zagg-client
OpenShift Tools Zagg Client Monitoring Scripts

%files monitoring-zagg-client
/usr/bin/cron-send-process-count
/usr/bin/ops-runner
/usr/bin/ops-zagg-client
%config(noreplace)/etc/openshift_tools/zagg_client.yaml


# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring-zagg-server subpackage
# ----------------------------------------------------------------------------------
%package monitoring-zagg-server
Summary:       OpenShift Tools Zagg Server Monitoring Scripts
Requires:      python2,python-openshift-tools-monitoring-zagg,python-openshift-tools-ansible
BuildRequires: python2-devel
BuildArch:     noarch

%description monitoring-zagg-server
OpenShift Tools Zagg Server Monitoring Scripts

%files monitoring-zagg-server
/usr/bin/ops-zagg-metric-processor
/usr/bin/ops-zagg-heartbeat-processor
/usr/bin/ops-zagg-heartbeater
/var/run/zagg/data
%config(noreplace)/etc/openshift_tools/zagg_server.yaml


# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring-aws subpackage
# ----------------------------------------------------------------------------------
%package monitoring-aws
Summary:       OpenShift Tools AWS Monitoring Scripts
Requires:      python2,python-openshift-tools-monitoring-aws,python-openshift-tools-monitoring-openshift,python-openshift-tools-monitoring-zagg
BuildRequires: python2-devel
BuildArch:     noarch

%description monitoring-aws
OpenShift Tools AWS Monitoring Scripts

%files monitoring-aws
/usr/bin/cron-send-s3-metrics


# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring-openshift subpackage
# ----------------------------------------------------------------------------------
%package monitoring-openshift
Summary:       OpenShift Tools Openshift Product Scripts
Requires:      python2,python-openshift-tools,python-openshift-tools-monitoring-openshift,python-openshift-tools-monitoring-zagg,openvswitch,python-dns
BuildRequires: python2-devel
BuildArch:     noarch

%description monitoring-openshift
OpenShift Tools Openshift Product Scripts

%files monitoring-openshift
%defattr(755,root,root)
/usr/bin/cron-event-watcher
/usr/bin/cron-send-ovs-status
/usr/bin/cron-send-etcd-status
/usr/bin/cron-send-os-master-metrics
/usr/bin/cron-send-create-app
/usr/bin/cron-send-project-stats
/usr/bin/cron-send-os-dnsmasq-checks
/usr/bin/cron-send-os-skydns-checks
/usr/bin/cron-send-registry-checks
/usr/bin/cron-openshift-pruner
/usr/bin/cron-send-cluster-capacity
/usr/bin/cron-send-connection-count
/usr/bin/cron-send-cpu-mem-stats
/usr/bin/cron-send-saml-status
/usr/bin/cron-certificate-expirations

# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring-zabbix-heal subpackage
# ----------------------------------------------------------------------------------
%package monitoring-zabbix-heal
Summary:       OpenShift Tools Zabbix Auto Heal Scripts
Requires:      python2
BuildRequires: python2-devel
BuildArch:     noarch

%description monitoring-zabbix-heal
OpenShift Tools Zabbix Auto Heal Scripts

%files monitoring-zabbix-heal
/usr/bin/ops-zbx-event-processor

# ----------------------------------------------------------------------------------
# openshift-tools-scripts-cloud-aws subpackage
# ----------------------------------------------------------------------------------
%package cloud-aws
Summary:       OpenShift Tools Cloud tools
Requires:      python2,python-openshift-tools-cloud-aws
BuildRequires: python2-devel
BuildArch:     noarch

%description cloud-aws
OpenShift Tools AWS specific scripts

%files cloud-aws
/usr/bin/ops-ec2-copy-ami-to-all-regions
/usr/bin/ops-ec2-snapshot-ebs-volumes
/usr/bin/ops-ec2-trim-ebs-snapshots
/usr/bin/ops-ec2-add-snapshot-tag-to-ebs-volumes

# ----------------------------------------------------------------------------------
# openshift-tools-scripts-cloud-gcp subpackage
# ----------------------------------------------------------------------------------
%package cloud-gcp
Summary:       OpenShift Tools Cloud tools
Requires:      python2,python-openshift-tools-cloud-gcp
BuildRequires: python2-devel
BuildArch:     noarch

%description cloud-gcp
OpenShift Tools GCP specific scripts

%files cloud-gcp
/usr/bin/ops-gcp-add-snapshot-label-to-pd-volumes
/usr/bin/ops-gcp-snapshot-pd-volumes
/usr/bin/ops-gcp-trim-pd-snapshots


%changelog
* Mon Sep 12 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.135-1
- Adding subpackage for gcp. (kwoodson@redhat.com)

* Mon Sep 12 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.134-1
- Adding gcp snapshot tooling. (kwoodson@redhat.com)

* Mon Sep 12 2016 Thomas Wiest <twiest@redhat.com> 0.0.133-1
- Added cgrouputil.py and changed dockerutil to be able to use it if requested.
  (twiest@redhat.com)

* Mon Sep 12 2016 Matt Woodson <mwoodson@redhat.com> 0.0.132-1
- don't need string defaults here, only in the to_* functions
  (dranders@redhat.com)
- pylint fail - line too long (on a comment, really?) :-( (dranders@redhat.com)
- underlying to_* functions require strings as defaults (dranders@redhat.com)
- misunderstood how defaults work with dict.get(key, default)
  (dranders@redhat.com)
- re-written to remove the if and just use math (dranders@redhat.com)
- set defaults in case if is never true (dranders@redhat.com)
- fix a max method (zhizhang@zhizhang-laptop-nay.redhat.com)
- use random project name, delete always at the end (sten@redhat.com)
- add Terminating project check (zhizhang@zhizhang-laptop-nay.redhat.com)

* Wed Aug 31 2016 Joel Diaz <jdiaz@redhat.com> 0.0.131-1
- don't include pre-cleanup task in timing of app creates (jdiaz@redhat.com)

* Wed Aug 31 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.130-1
- Moving default behavoir to use cache for ossh and oscp (kwoodson@redhat.com)

* Mon Aug 29 2016 Sten Turpin <sten@redhat.com> 0.0.129-1
- added function to delete ES index after app create (sten@redhat.com)

* Mon Aug 29 2016 Joel Diaz <jdiaz@redhat.com> 0.0.128-1
- Added cron-send-docker-containers-usage.py (twiest@redhat.com)
- grab the actual docker-timer script (jdiaz@redhat.com)

* Tue Aug 23 2016 Joel Diaz <jdiaz@redhat.com> 0.0.127-1
- script to report on age of certificates (jdiaz@redhat.com)

* Fri Aug 19 2016 Zhiming Zhang <zhizhang@redhat.com> 0.0.126-1
- Add more container info to existing dns resolution check output
  (agrimm@redhat.com)
- Prune haproxy processes more aggressively (agrimm@redhat.com)
- add saml check (zhizhang@zhizhang-laptop-nay.redhat.com)

* Mon Aug 15 2016 Joel Diaz <jdiaz@redhat.com> 0.0.125-1
- change logic to simply stop any haproxy process... (jdiaz@redhat.com)

* Fri Aug 12 2016 Joel Diaz <jdiaz@redhat.com> 0.0.124-1
- script to identify and stop stuck haproxy processes (jdiaz@redhat.com)
- add try and timestamps around zgs_send (sten@redhat.com)
- print timestamp on app create start (sten@redhat.com)

* Wed Jul 27 2016 Wesley Hearn <whearn@redhat.com> 0.0.123-1
- Print first IP address in json output. convert_to_ip will return 1 ip address
  in our use case (whearn@redhat.com)

* Wed Jul 27 2016 Wesley Hearn <whearn@redhat.com> 0.0.121-1
- Added simple json output to ohi, updated awsutil to have convert_to_ip not
  require a list (whearn@redhat.com)

* Mon Jul 25 2016 Joel Diaz <jdiaz@redhat.com> 0.0.120-1
- add synthetic cluster-wide host support to ops-zagg-client (jdiaz@redhat.com)
- moving everything from dynamic keys to static zabbix items
  (ihorvath@redhat.com)
- Moved unncecesary output to only display on verbose mode
  (bshpurke@redhat.com)
- Improved nodes_not_schedulable check Check avoids master nodes Reincluded
  zabbix trigger for check (bshpurke@redhat.com)
- etcd metrics with dynamic items in zabbix (ihorvath@redhat.com)

* Mon Jul 25 2016 Joel Diaz <jdiaz@redhat.com>
- add synthetic cluster-wide host support to ops-zagg-client (jdiaz@redhat.com)
- moving everything from dynamic keys to static zabbix items
  (ihorvath@redhat.com)
- Moved unncecesary output to only display on verbose mode
  (bshpurke@redhat.com)
- Improved nodes_not_schedulable check Check avoids master nodes Reincluded
  zabbix trigger for check (bshpurke@redhat.com)
- etcd metrics with dynamic items in zabbix (ihorvath@redhat.com)

* Tue Jul 19 2016 Joel Diaz <jdiaz@redhat.com> 0.0.118-1
- add --timeout to ops-runner and a dynamic item to hold these items
  (jdiaz@redhat.com)
- better readability, same refactor for oadm (sten@redhat.com)
- refactor to use subprocess.communicate(), capture all pod logs in the project
  on failure (sten@redhat.com)
- return all pod logs (sten@redhat.com)
- add --list-cluster to ohi (sten@redhat.com)

* Thu Jul 07 2016 Russell Harrison <rharriso@redhat.com> 0.0.117-1
- Removed unused sys import (rharriso@redhat.com)
- Remove rev bump (rharriso@redhat.com)
- Add basic dnsmasq monitoring template and cron configuration
  (rharriso@redhat.com)

* Thu Jul 07 2016 Joel Diaz <jdiaz@redhat.com> 0.0.116-1
- add new cluster-wide calculations 1) cluster-wide max allocatable memory (for
  compute nodes) 2) cluster-wide max cpu (for compute nodes) in milicores 3)
  cluster-wide cpu units scheduled across compute nodes (total in milicores and
  percentage) 4) cluster-wide cpu unscheduled resources across compute nodes
  (total in milicores and percentage) 5) cluster-wide mem scheduled across
  compute nodes (total in bytes and percentage) 6) cluster-wide mem unscheduled
  resources across compute nodes (total in bytes and percentage) 7) cluster-
  wide cpu and memory oversubscription (using cpu/mem limits on running pods)
  (jdiaz@redhat.com)

* Wed Jul 06 2016 Joel Diaz <jdiaz@redhat.com> 0.0.115-1
- Illiminated unnecessary for loop (benpack101@gmail.com)
- Fixed pylint issues (benpack101@gmail.com)
- Added check for nodes without labels (bshpurke@redhat.com)
- send integers to zabbix (that's what it expects) (jdiaz@redhat.com)

* Wed Jul 06 2016 Ivan Horvath <ihorvath@redhat.com> 0.0.114-1
- adding cpu and memory per process monitoring (ihorvath@redhat.com)
- adding new cpu/mem percentage monitoring script (ihorvath@redhat.com)
- adding cpu and memory per process monitoring (ihorvath@redhat.com)
- adding new cpu/mem percentage monitoring script (ihorvath@redhat.com)
- add event watching script to RPM (jdiaz@redhat.com)

* Tue Jul 05 2016 Sten Turpin <sten@redhat.com> 0.0.113-1
- added debug info for nodes not ready check (sten@redhat.com)
- Making refresh-cache work in oscp ossh. (kwoodson@redhat.com)
- report average cpu and memory allocations for compute nodes across the
  cluster (jdiaz@redhat.com)
- add flock without erroring on lock already acquired (jdiaz@redhat.com)
- openshift event watcher/reporter (jdiaz@redhat.com)

* Fri Jun 24 2016 Zhiming Zhang <zhizhang@redhat.com> 0.0.112-1
- just in order to build new rpm (zhizhang@zhizhang-laptop-nay.redhat.com)

* Thu Jun 23 2016 Joel Diaz <jdiaz@redhat.com> 0.0.111-1
- gracefully handle nodes with no 'type' label (jdiaz@redhat.com)

* Thu Jun 23 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.110-1
- deal will nodes with no running pods (jdiaz@redhat.com)
- move the script to right rpm (zhizhang@zhizhang-laptop-nay.redhat.com)

* Thu Jun 23 2016 zhiming
-

* Wed Jun 22 2016 Joel Diaz <jdiaz@redhat.com> 0.0.108-1
- catch ocassional exception on container cleanup (and retry)
  (jdiaz@redhat.com)

* Tue Jun 21 2016 Thomas Wiest <twiest@redhat.com> 0.0.107-1
- Added Name and purpose tagging to ops-ec2-add-snapshot-tag-to-ebs-volumes.py
  (twiest@redhat.com)

* Mon Jun 20 2016 Joel Diaz <jdiaz@redhat.com> 0.0.106-1
- fixed handling urlerror, added timeout (sten@redhat.com)

* Mon Jun 20 2016 Joel Diaz <jdiaz@redhat.com> 0.0.105-1
- handle case when no clusterrolebinding is defined (return code non-zero)
  (jdiaz@redhat.com)

* Fri Jun 17 2016 Ivan Horvath <ihorvath@redhat.com> 0.0.104-1
- changing the cron entries, because they were lacking the names and adding
  defattr to files section in one of the packages in the script spec file
  (ihorvath@redhat.com)

* Wed Jun 15 2016 Ivan Horvath <ihorvath@redhat.com> 0.0.103-1
- fixing typo in path inside script spec file (ihorvath@redhat.com)

* Wed Jun 15 2016 Unknown name 0.0.102-1
- Adding monitoring for existing connections on etcd and master api server
  (ihorvath@redhat.com)

* Wed Jun 08 2016 Thomas Wiest <twiest@redhat.com> 0.0.101-1
- Added ops-ec2-add-snapshot-tag-to-ebs-volumes.py (twiest@redhat.com)
- fix for the s3 docker registry (mwoodson@redhat.com)

* Thu Jun 02 2016 Sten Turpin <sten@redhat.com> 0.0.100-1
- specify known-good version of hello-openshift (sten@redhat.com)

* Wed Jun 01 2016 Sten Turpin <sten@redhat.com> 0.0.99-1
- moved app build check into cron-send-create-app

* Wed Jun 01 2016 Sten Turpin <sten@redhat.com> 0.0.98-1
- remove cron-send-build-app script (sten@redhat.com)
- added build/arbitrary app create capability to create-app check
  (sten@redhat.com)

* Wed Jun 01 2016 Joel Diaz <jdiaz@redhat.com> 0.0.97-1
- ignore non-ready nodes (jdiaz@redhat.com)

* Tue May 31 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.96-1
- Fixing list functionality when oo vars are missing (kwoodson@redhat.com)
- add cpu check for process (zhizhang@zhizhang-laptop-nay.redhat.com)

* Tue May 31 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.95-1
-

* Fri May 27 2016 Joel Diaz <jdiaz@redhat.com> 0.0.94-1
- cluster-capacity script relies on base python-openshift-tools/conversions.py
  (jdiaz@redhat.com)
- allow capacity checks on 3.1 clusters (jdiaz@redhat.com)
- memory available and max-mem pod schedulable capacity checks plus new
  'conversions' library and necessary RPM spec updates to include capacity
  checks into monitoring-openshift.rpm (jdiaz@redhat.com)

* Tue May 24 2016 Joel Diaz <jdiaz@redhat.com> 0.0.93-1
- 'try' each pruning attempt so an earlier error doesn't stop all pruning
  (jdiaz@redhat.com)
- use oadm instead of oc as a workaround for 3.2 (sten@redhat.com)
- demo using oadm to create project (sten@redhat.com)
- 10 minutes for build, 4 minutes for deploy (sten@redhat.com)

* Thu May 19 2016 Joel Diaz <jdiaz@redhat.com> 0.0.92-1
- add build/deploy/image pruning script (jdiaz@redhat.com)

* Thu May 19 2016 Matt Woodson <mwoodson@redhat.com> 0.0.91-1
- fixed the aws s3 check (mwoodson@redhat.com)

* Wed May 18 2016 Matt Woodson <mwoodson@redhat.com> 0.0.90-1
- fixed a skydns issue (mwoodson@redhat.com)

* Wed May 18 2016 Matt Woodson <mwoodson@redhat.com> 0.0.89-1
- shortening the project name in the cron-send-build-app.py
  (mwoodson@redhat.com)

* Mon May 16 2016 Thomas Wiest <twiest@redhat.com> 0.0.88-1
- Added ops-ec2-snapshot-ebs-volumes.py and ops-ec2-trim-ebs-snapshots.py
  (twiest@redhat.com)
- added a function to prevent running outside bastion hosts (sten@redhat.com)
- fixed comments referring to the check this was based on (sten@redhat.com)
- pylint.... (sten@redhat.com)
- add kubeconfig test (sten@redhat.com)
- a little cleanup as suggested by mwoodson (sten@redhat.com)
- fixed pylint errors (sten@redhat.com)
- script to generate + request signing of certs (sten@redhat.com)
- renamed build-local-setup.sh to build-local-setup-centos7.sh and fixed it to
  work with our latest way to build. Also fixed the
  local_development_monitoring.adoc to be in line with our current way of
  developing. (twiest@redhat.com)

* Fri Apr 22 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.87-1
- Kubeconfig fix (kwoodson@redhat.com)
- fix up references to openshift-ansible repo (jdiaz@redhat.com)

* Mon Apr 18 2016 Joel Diaz <jdiaz@redhat.com> 0.0.86-1
- chmod +x for all the executable files in scripts-inventory-clients RPM and
  pylint fixes (jdiaz@redhat.com)

* Mon Apr 18 2016 Joel Diaz <jdiaz@redhat.com> 0.0.85-1
- fix dependency name, and switch to not depend on openshift-ansible*
  (jdiaz@redhat.com)

* Mon Apr 18 2016 Joel Diaz <jdiaz@redhat.com> 0.0.84-1
- copy host/inventory tools from openshift-ansible/bin and generate equivalent
  RPMs clean up pylint (jdiaz@redhat.com)
- found + fixed a typo (sten@redhat.com)
- fixed pylint errors (sten@redhat.com)
- add pod and web service checks (sten@redhat.com)

* Thu Mar 24 2016 Unknown name 0.0.83-1
- disable line-too-long on line 384 (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix pylint space (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix some pylint last (zhizhang@redhat.com)
- fix some pylint 2 (zhizhang@redhat.com)
- fix some pylint (zhizhang@redhat.com)
- delete some useless code (zhizhang@redhat.com)
- fix some dynamic error (zhizhang@redhat.com)
- fix some typo (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix line too long (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix some pylint space problem (zhizhang@zhizhang-laptop-nay.redhat.com)
- add two item pv.capacity total and available capacity andd dynamic pv.count
  (zhizhang@zhizhang-laptop-nay.redhat.com)
- also fail if there's no ready status (sten@redhat.com)
- loop over conditions instead of checking only the first (sten@redhat.com)

* Tue Mar 15 2016 Joel Diaz <jdiaz@redhat.com> 0.0.82-1
- Adding verbosity to simple app create (kwoodson@redhat.com)

* Mon Mar 14 2016 Joel Diaz <jdiaz@redhat.com> 0.0.81-1
- zagg-server doesn't need monitoring-openshift (jdiaz@redhat.com)

* Thu Mar 03 2016 Unknown name 0.0.80-1
- add the cron-send-build-app to the list (zhizhang@zhizhang-laptop-
  nay.redhat.com)

* Thu Mar 03 2016 Unknown name 0.0.79-1
- remove some useless var (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix another bug (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix some faile bug (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix the build time of fail (zhizhang@zhizhang-laptop-nay.redhat.com)
- add buildtime when build error (zhizhang@zhizhang-laptop-nay.redhat.com)
- remove the verbose (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix some verbose (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix unused i (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix too-many-branch (zhizhang@zhizhang-laptop-nay.redhat.com)
- delete some space after # (zhizhang@zhizhang-laptop-nay.redhat.com)
- disable pylint=too-many-branches (zhizhang@zhizhang-laptop-nay.redhat.com)
- add more function try to solve the oo many branches (zhizhang@zhizhang-
  laptop-nay.redhat.com)
- fix the Unused variable (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix Tab (zhizhang@zhizhang-laptop-nay.redhat.com)
- fix python Tab and space problem (zhizhang@zhizhang-laptop-nay.redhat.com)
- send both the app create time and build time to zabbix (zhizhang@zhizhang-
  laptop-nay.redhat.com)
- fix some bugs of checking (zhizhang@zhizhang-laptop-nay.redhat.com)
- checking app create on master with a build process (zhizhang@zhizhang-laptop-
  nay.redhat.com)

* Fri Feb 19 2016 Matt Woodson <mwoodson@redhat.com> 0.0.78-1
- changed the url to look for the api for master api check
  (mwoodson@redhat.com)
- fix up the error/exception handing path (jdiaz@redhat.com)

* Thu Feb 18 2016 Joel Diaz <jdiaz@redhat.com> 0.0.77-1
- deal with secure and non-secure registries (jdiaz@redhat.com)

* Wed Feb 17 2016 Joel Diaz <jdiaz@redhat.com> 0.0.76-1
- docker-registry health script (for master and non-master) (jdiaz@redhat.com)

* Tue Feb 16 2016 Joel Diaz <jdiaz@redhat.com> 0.0.75-1
- make sure regex matches trigger name (jdiaz@redhat.com)

* Tue Feb 16 2016 Joel Diaz <jdiaz@redhat.com> 0.0.74-1
- add step to re-run OVS report after fix is complete (jdiaz@redhat.com)

* Mon Feb 15 2016 Matt Woodson <mwoodson@redhat.com> 0.0.73-1
- pylint: ignore module name (mwoodson@redhat.com)
- changed the ec2 ami copy script name (mwoodson@redhat.com)

* Mon Feb 15 2016 Matt Woodson <mwoodson@redhat.com> 0.0.72-1
- added ec2_copy_ami_to_regions.py; added the cloud rpm (mwoodson@redhat.com)
- add ops-runner id name to logged output (jdiaz@redhat.com)

* Tue Feb 09 2016 Sten Turpin <sten@redhat.com> 0.0.71-1
- registry check now works on old + new registry, and checks all available
  registries (sten@redhat.com)

* Tue Feb 09 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.70-1
- Adding file to list of file in rpm (kwoodson@redhat.com)

* Tue Feb 09 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.69-1
- App create updates for multi-master (kwoodson@redhat.com)

* Mon Feb 08 2016 Joel Diaz <jdiaz@redhat.com> 0.0.68-1
- fix rename of remote-heal to remote-healer (jdiaz@redhat.com)

* Mon Feb 08 2016 Joel Diaz <jdiaz@redhat.com> 0.0.67-1
- add missing config file (jdiaz@redhat.com)

* Mon Feb 08 2016 Joel Diaz <jdiaz@redhat.com> 0.0.66-1
- fix bad variable name (jdiaz@redhat.com)

* Mon Feb 08 2016 Joel Diaz <jdiaz@redhat.com> 0.0.65-1
- add missing bits to spec (jdiaz@redhat.com)
- 2nd attempt remote healing tool (jdiaz@redhat.com)

* Thu Feb 04 2016 Sten Turpin <sten@redhat.com> 0.0.64-1
- registry no longer sends {} (sten@redhat.com)
- renamed /etc/openshift to /etc/origin (sten@redhat.com)
- new master check for hosts not ready
* Mon Feb 01 2016 Joel Diaz <jdiaz@redhat.com> 0.0.63-1
- report stray OVS rules found before and after cleanup (jdiaz@redhat.com)

* Mon Feb 01 2016 Matt Woodson <mwoodson@redhat.com> 0.0.62-1
- change master check to look for cluster api url; added master local check as
  well (mwoodson@redhat.com)

* Thu Jan 28 2016 Thomas Wiest <twiest@redhat.com> 0.0.61-1
- fixed bug in ops-runner when sending items to zabbix. (twiest@redhat.com)

* Wed Jan 27 2016 Thomas Wiest <twiest@redhat.com> 0.0.60-1
- Converted ops-runner from bash to python. (twiest@redhat.com)

* Wed Jan 27 2016 Joel Diaz <jdiaz@redhat.com> 0.0.59-1
- fix typo RPM dependency (jdiaz@redhat.com)

* Wed Jan 27 2016 Joel Diaz <jdiaz@redhat.com> 0.0.58-1
- add script (and new RPM) to detect and remove stray OVS rules/flows
  (jdiaz@redhat.com)

* Wed Jan 27 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.57-1
-

* Tue Jan 26 2016 Joel Diaz <jdiaz@redhat.com> 0.0.56-1
- improve quoting of passed in arguments (jdiaz@redhat.com)

* Tue Jan 26 2016 Matt Woodson <mwoodson@redhat.com> 0.0.55-1
- fixed import dns stuff (mwoodson@redhat.com)

* Tue Jan 26 2016 Matt Woodson <mwoodson@redhat.com> 0.0.54-1
- added the skydns checks (mwoodson@redhat.com)
- Adding support for master ha checks (kwoodson@redhat.com)

* Mon Jan 25 2016 Joel Diaz <jdiaz@redhat.com> 0.0.53-1
- be more careful with mktemp and logging (fall back to logger)
  (jdiaz@redhat.com)

* Mon Jan 25 2016 Thomas Wiest <twiest@redhat.com> 0.0.52-1
- Added flock capabilities to ops-runner. (twiest@redhat.com)

* Thu Jan 21 2016 Joel Diaz <jdiaz@redhat.com> 0.0.51-1
- log non-zero exits to /var/log/ops-runner.log (jdiaz@redhat.com)

* Tue Jan 19 2016 Matt Woodson <mwoodson@redhat.com> 0.0.50-1
- separated pcp from zagg sender (mwoodson@redhat.com)

* Mon Jan 18 2016 Matt Woodson <mwoodson@redhat.com> 0.0.49-1
- removed python-openshift-tools-ansible as a dependency for ops-zagg-client
  (mwoodson@redhat.com)

* Mon Jan 18 2016 Matt Woodson <mwoodson@redhat.com> 0.0.48-1
- removed some old rpm references (mwoodson@redhat.com)

* Mon Jan 18 2016 Matt Woodson <mwoodson@redhat.com> 0.0.47-1
- sepearated openshift-tools rpms into subpackages (mwoodson@redhat.com)

* Mon Jan 11 2016 Matt Woodson <mwoodson@redhat.com> 0.0.46-1
- changed the dns resolution check's docker container to reference
  (mwoodson@redhat.com)

* Mon Jan 04 2016 Joel Diaz <jdiaz@redhat.com> 0.0.45-1
- have seen getent take up to 80 sec to complete raise timeout to allow it to
  finish (jdiaz@redhat.com)

* Thu Dec 17 2015 Joel Diaz <jdiaz@redhat.com> 0.0.44-1
- make script executable (jdiaz@redhat.com)

* Thu Dec 17 2015 Joel Diaz <jdiaz@redhat.com> 0.0.43-1
- script and cron to test DNS resolution on exising containers
  (jdiaz@redhat.com)

* Wed Dec 16 2015 Thomas Wiest <twiest@redhat.com> 0.0.42-1
- Split ops-zagg-processor.py into ops-zagg-metric-processor.py and ops-zagg-
  heartbeat-processor.py. (twiest@redhat.com)

* Wed Dec 16 2015 Joel Diaz <jdiaz@redhat.com> 0.0.41-1
- change to using oso-rhel7-zagg-client container and hit redhat.com instead of
  google.com (jdiaz@redhat.com)

* Tue Dec 15 2015 Joel Diaz <jdiaz@redhat.com> 0.0.40-1
- script to test and report DNS query results within container
  (jdiaz@redhat.com)

* Mon Dec 14 2015 Matt Woodson <mwoodson@redhat.com> 0.0.39-1
- added random sleep to heartbeats checks (mwoodson@redhat.com)
- added random sleep to ops-runner (mwoodson@redhat.com)

* Mon Dec 14 2015 Joel Diaz <jdiaz@redhat.com> 0.0.38-1
- Changed ops-zagg-processor to send metrics on the number of metrics in the
  queue, heart beats in the queue and the number of errors while processing.
  (twiest@redhat.com)
- Add script to be called from zabbix custom script actions and lay down config
  file for it during playbook run (jdiaz@redhat.com)

* Tue Dec 08 2015 Thomas Wiest <twiest@redhat.com> 0.0.37-1
- Added chunking and error handling to ops-zagg-processor for zabbix targets.
  (twiest@redhat.com)

* Fri Dec 04 2015 Matt Woodson <mwoodson@redhat.com> 0.0.36-1
- added pv counts to the master openshift api check (mwoodson@redhat.com)

* Wed Dec 02 2015 Matt Woodson <mwoodson@redhat.com> 0.0.35-1
- added docker registry cluster check (mwoodson@redhat.com)

* Fri Nov 20 2015 Matt Woodson <mwoodson@redhat.com> 0.0.34-1
- added nan check (mwoodson@redhat.com)

* Thu Nov 19 2015 Matt Woodson <mwoodson@redhat.com> 0.0.33-1
- grouped the checks and wrapped them in try/except (mwoodson@redhat.com)
- added openshift api ping check to master check script (mwoodson@redhat.com)
- added metrics to cron-send-os-master (mwoodson@redhat.com)

* Tue Nov 17 2015 Matt Woodson <mwoodson@redhat.com> 0.0.32-1
- fixed the healthz check (mwoodson@redhat.com)

* Tue Nov 17 2015 Matt Woodson <mwoodson@redhat.com> 0.0.31-1
- changed permissions, fixed a bug of master api check (mwoodson@redhat.com)

* Tue Nov 17 2015 Joel Diaz <jdiaz@redhat.com> 0.0.30-1
- Docker cron timing (jdiaz@redhat.com)

* Tue Nov 17 2015 Matt Woodson <mwoodson@redhat.com> 0.0.29-1
- removed old scripts (mwoodson@redhat.com)
- added some updated rest api; added user running pod count
  (mwoodson@redhat.com)
- updated the spec and cron jobs to run the new master api check
  (mwoodson@redhat.com)
- added the openshift rest api, updated master script (mwoodson@redhat.com)
- added master monitoring (mwoodson@redhat.com)

* Mon Nov 16 2015 Joel Diaz <jdiaz@redhat.com> 0.0.28-1
- Add scripts to report S3 bucket stats from master nodes (jdiaz@redhat.com)

* Tue Nov 10 2015 Marek Mahut <mmahut@redhat.com> 0.0.27-1
- Load the etcd port as it can be different when using external etcd
  (mmahut@redhat.com)

* Fri Nov 06 2015 Matt Woodson <mwoodson@redhat.com> 0.0.26-1
- added network checks (mwoodson@redhat.com)

* Wed Nov 04 2015 Matt Woodson <mwoodson@redhat.com> 0.0.25-1
- added %%util check to disk checker (mwoodson@redhat.com)

* Wed Nov 04 2015 Marek Mahut <mmahut@redhat.com> 0.0.24-1
- sbin/bash doesn't exist (mmahut@redhat.com)
- Make sure cron-send-project-count.sh is executable (mmahut@redhat.com)

* Tue Nov 03 2015 Matt Woodson <mwoodson@redhat.com> 0.0.23-1
- added the disk tps check (mwoodson@redhat.com)

* Tue Nov 03 2015 Marek Mahut <mmahut@redhat.com> 0.0.22-1
- Adding the cron-send-etcd-status.py tool and its dependencies
  (mmahut@redhat.com)

* Mon Nov 02 2015 Joel Diaz <jdiaz@redhat.com> 0.0.21-1
- add scripts to check and report pcp ping state. update zagg-client playbooks
  to add cron job for checking pcp ping state (jdiaz@redhat.com)

* Mon Nov 02 2015 Unknown name 0.0.20-1
-

* Fri Oct 30 2015 Unknown name 0.0.19-1
- Update cron-send-project-count.sh (gburges@redhat.com)
- Update cron-send-project-count.sh (gburges@redhat.com)
- finally done(?) (gburges@redhat.com)

* Mon Oct 12 2015 Matt Woodson <mwoodson@redhat.com> 0.0.18-1
- added pcp derived items; added debug and verbose (mwoodson@redhat.com)

* Thu Oct 08 2015 Sten Turpin <sten@redhat.com> 0.0.17-1
- make keys for data being sent match with what was defined in zabbix
  (sten@redhat.com)
- added cron-send-ovs-status script + accompanying changes (sten@redhat.com)
- added http to https redirect (sten@redhat.com)

* Thu Oct 08 2015 Thomas Wiest <twiest@redhat.com> 0.0.16-1
- Corrected the count script to properly return exit codes
  (mwhittingham@redhat.com)
- A few bug fixes (mwhittingham@redhat.com)

* Thu Oct 08 2015 Thomas Wiest <twiest@redhat.com> 0.0.15-1
- Send a count of users to Zabbix (mwhittingham@redhat.com)

* Fri Oct 02 2015 Thomas Wiest <twiest@redhat.com> 0.0.14-1
- added ops-runner. It sends the exit code of the command to zabbix.
  (twiest@redhat.com)

* Wed Sep 30 2015 Kenny Woodson <kwoodson@redhat.com> 0.0.13-1
- Adding a pcp metric sampler for cpu stats (kwoodson@redhat.com)

* Mon Sep 28 2015 Matt Woodson <mwoodson@redhat.com> 0.0.12-1
- changed underscores to hyphen (mwoodson@redhat.com)

* Fri Sep 25 2015 Matt Woodson <mwoodson@redhat.com> 0.0.11-1
- fixed the spec file (mwoodson@redhat.com)

* Fri Sep 25 2015 Matt Woodson <mwoodson@redhat.com> 0.0.10-1
- added dynamic prototype support to zagg. added the filsystem checks to use
  this (mwoodson@redhat.com)

* Thu Sep 17 2015 Thomas Wiest <twiest@redhat.com> 0.0.9-1
- added cron-send-process-count.sh and checks for openshift master and node
  processes are up. (twiest@redhat.com)

* Wed Sep 16 2015 Kenny Woodson <kwoodson@redhat.com> 0.0.8-1
- Adding SSL support for v3 monitoring (kwoodson@redhat.com)

* Tue Aug 18 2015 Matt Woodson <mwoodson@redhat.com> 0.0.7-1
- Merge pull request #20 from jgkennedy/pr (twiest@users.noreply.github.com)
- Combined the two graphs and refactored some things (jessek@redhat.com)

* Fri Jul 31 2015 Matt Woodson <mwoodson@redhat.com> 0.0.6-1
-

* Fri Jul 31 2015 Thomas Wiest <twiest@redhat.com> 0.0.5-1
- added zagg to zagg capability to ops-zagg-processor (twiest@redhat.com)

* Thu Jul 23 2015 Thomas Wiest <twiest@redhat.com> 0.0.4-1
- added ops-zagg-heartbeater.py (twiest@redhat.com)

* Wed Jul 15 2015 Thomas Wiest <twiest@redhat.com> 0.0.3-1
- added config file for ops-zagg-processor (twiest@redhat.com)

* Wed Jul 15 2015 Thomas Wiest <twiest@redhat.com> 0.0.2-1
- added python-openshift-tools-ansible sub package. (twiest@redhat.com)
- changed openshift-tools-scripts spec file to automatically include all
  monitoring scripts. (twiest@redhat.com)
- added ops-zagg-processor.py (twiest@redhat.com)
- added openshift-tools-scripts.spec (twiest@redhat.com)
* Tue Jul 07 2015 Thomas Wiest <twiest@redhat.com> 0.0.1-1
- new package built with tito
