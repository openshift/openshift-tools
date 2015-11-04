Summary:       OpenShift Tools Scripts
Name:          openshift-tools-scripts
Version:       0.0.24
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
cp -p monitoring/ops-zagg-processor.py %{buildroot}/usr/bin/ops-zagg-processor
cp -p monitoring/ops-zagg-heartbeater.py %{buildroot}/usr/bin/ops-zagg-heartbeater
cp -p monitoring/cron-send-process-count.sh %{buildroot}/usr/bin/cron-send-process-count
cp -p monitoring/cron-send-filesystem-metrics.py %{buildroot}/usr/bin/cron-send-filesystem-metrics
cp -p monitoring/cron-send-pcp-sampled-metrics.py %{buildroot}/usr/bin/cron-send-pcp-sampled-metrics
cp -p monitoring/ops-runner.sh %{buildroot}/usr/bin/ops-runner
cp -p monitoring/cron-send-user-count.sh %{buildroot}/usr/bin/cron-send-user-count
cp -p monitoring/cron-send-pod-count.py %{buildroot}/usr/bin/cron-send-pod-count
cp -p monitoring/cron-send-ovs-status.py %{buildroot}/usr/bin/cron-send-ovs-status
cp -p monitoring/cron-send-project-count.sh %{buildroot}/usr/bin/cron-send-project-count
cp -p monitoring/cron-send-pcp-ping.sh %{buildroot}/usr/bin/cron-send-pcp-ping
cp -p monitoring/cron-send-etcd-status.py %{buildroot}/usr/bin/cron-send-etcd-status
cp -p monitoring/cron-send-disk-metrics.py %{buildroot}/usr/bin/cron-send-disk-metrics

mkdir -p %{buildroot}/etc/openshift_tools
cp -p monitoring/zagg_client.yaml.example %{buildroot}/etc/openshift_tools/zagg_client.yaml
cp -p monitoring/zagg_server.yaml.example %{buildroot}/etc/openshift_tools/zagg_server.yaml

mkdir -p %{buildroot}/var/run/zagg/data


# ----------------------------------------------------------------------------------
# openshift-tools-scripts-monitoring subpackage
# ----------------------------------------------------------------------------------
%package monitoring
Summary:       OpenShift Tools Monitoring Scripts
Requires:      python2,python-openshift-tools-monitoring,python-openshift-tools-ansible
BuildRequires: python2-devel
BuildArch:     noarch

%description monitoring
OpenShift Tools Monitoring Scripts

%files monitoring
/usr/bin/*
%config(noreplace)/etc/openshift_tools/*.yaml
/var/run/zagg/
/var/run/zagg/data/

%changelog
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
