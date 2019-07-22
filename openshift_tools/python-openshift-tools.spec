Summary:       OpenShift Tools Python Package
Name:          python-openshift-tools
Version:       0.0.145
Release:       1%{?dist}
License:       ASL 2.0
URL:           https://github.com/openshift/openshift-tools
Source0:       %{name}-%{version}.tar.gz
Requires:      python2
BuildRequires: python2-devel
BuildArch:     noarch

%description
OpenShift Tools Python Package

%prep
%setup -q

%build

%install
# openshift_tools install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools
cp -p *.py %{buildroot}%{python_sitelib}/openshift_tools/

# openshift_tools/cloud install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/cloud
cp -p cloud/*.py %{buildroot}%{python_sitelib}/openshift_tools/cloud

# openshift_tools/cloud/aws install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/cloud/aws
cp -p cloud/aws/*.py %{buildroot}%{python_sitelib}/openshift_tools/cloud/aws

# openshift_tools/cloud/gcp install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/cloud/gcp
cp -p cloud/gcp/*.py %{buildroot}%{python_sitelib}/openshift_tools/cloud/gcp

# openshift_tools/monitoring install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/monitoring
cp -p monitoring/*.py %{buildroot}%{python_sitelib}/openshift_tools/monitoring

# openshift_tools/ansible install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/ansible
cp -p ansible/*.py %{buildroot}%{python_sitelib}/openshift_tools/ansible

# openshift_tools/web install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/web
cp -p web/*.py %{buildroot}%{python_sitelib}/openshift_tools/web

# openshift_tools/zbxapi install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/zbxapi
cp -p zbxapi/*.py %{buildroot}%{python_sitelib}/openshift_tools/zbxapi

# openshift_tools/utils
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/utils
cp -p utils/*.py %{buildroot}%{python_sitelib}/openshift_tools/utils

# openshift_tools/inventory_clients install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/inventory_clients
cp -pP inventory_clients/* %{buildroot}%{python_sitelib}/openshift_tools/inventory_clients
# symlinks work within git repo, but we need to fix them when installing the RPM
rm %{buildroot}%{python_sitelib}/openshift_tools/inventory_clients/multi_inventory.py
rm %{buildroot}%{python_sitelib}/openshift_tools/inventory_clients/aws
rm %{buildroot}%{python_sitelib}/openshift_tools/inventory_clients/gce
ln -s %{_datadir}/ansible/inventory/multi_inventory.py %{buildroot}%{python_sitelib}/openshift_tools/inventory_clients/multi_inventory.py
ln -s %{_datadir}/ansible/inventory/aws %{buildroot}%{python_sitelib}/openshift_tools/inventory_clients/aws
ln -s %{_datadir}/ansible/inventory/gce %{buildroot}%{python_sitelib}/openshift_tools/inventory_clients/gce


# openshift_tools files
%files
%dir %{python_sitelib}/openshift_tools
%dir %{python_sitelib}/openshift_tools/monitoring
%{python_sitelib}/openshift_tools/monitoring/__init*
%{python_sitelib}/openshift_tools/*.py
%{python_sitelib}/openshift_tools/*.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-inventory-clients subpackage
# ----------------------------------------------------------------------------------
%package inventory-clients
Summary:       OpenShift Tools Python libs for inventory clients
Requires:      python2,openshift-tools-ansible-inventory-aws,openshift-tools-ansible-inventory-gce,python-openshift-tools
BuildArch:     noarch

%description inventory-clients
OpenShift Tools Python libraries for inventory clients

%files inventory-clients
%{python_sitelib}/openshift_tools/inventory_clients/*


# ----------------------------------------------------------------------------------
# python-openshift-tools-monitoring-pcp subpackage
# ----------------------------------------------------------------------------------
%package monitoring-pcp
Summary:       OpenShift Tools PCP Python Library Package
Requires:      python2,python-openshift-tools,python-pcp
BuildArch:     noarch

%description monitoring-pcp
PCP Python libraries developed for monitoring OpenShift.

%files monitoring-pcp
%{python_sitelib}/openshift_tools/monitoring/pminfo*.py
%{python_sitelib}/openshift_tools/monitoring/pminfo*.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-monitoring-docker subpackage
# ----------------------------------------------------------------------------------
%package monitoring-docker
Summary:       OpenShift Tools Docker Python Libraries Package
Requires:      python2,python-openshift-tools,python-pcp
BuildArch:     noarch

%description monitoring-docker
Docker Python libraries developed for monitoring OpenShift.

%files monitoring-docker
%{python_sitelib}/openshift_tools/monitoring/dockerutil.py
%{python_sitelib}/openshift_tools/monitoring/dockerutil.py[co]


# ----------------------------------------------------------------------------------
# python-openshift-tools-monitoring-zagg subpackage
# ----------------------------------------------------------------------------------
%package monitoring-zagg
Summary:       OpenShift Tools Zagg Python Libraries Package
Requires:      python2,python-openshift-tools,python-openshift-tools-web,python-zbxsend,python-redis
BuildArch:     noarch

%description monitoring-zagg
Zagg Python libraries developed for monitoring OpenShift.

%files monitoring-zagg
%{python_sitelib}/openshift_tools/monitoring/metricmanager.py
%{python_sitelib}/openshift_tools/monitoring/metricmanager.py[co]
%{python_sitelib}/openshift_tools/monitoring/zagg*.py
%{python_sitelib}/openshift_tools/monitoring/zagg*.py[co]
%{python_sitelib}/openshift_tools/monitoring/zabbix_metric_processor.py
%{python_sitelib}/openshift_tools/monitoring/zabbix_metric_processor.py[co]
%{python_sitelib}/openshift_tools/monitoring/generic_metric_sender.py
%{python_sitelib}/openshift_tools/monitoring/generic_metric_sender.py[co]
%{python_sitelib}/openshift_tools/monitoring/metric_sender.py
%{python_sitelib}/openshift_tools/monitoring/metric_sender.py[co]
%{python_sitelib}/openshift_tools/monitoring/hawk*.py
%{python_sitelib}/openshift_tools/monitoring/hawk*.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-monitoring-aws subpackage
# ----------------------------------------------------------------------------------
%package monitoring-aws
Summary:       OpenShift Tools AWS Python Libraries Package
Requires:      python2,python-openshift-tools,python-awscli
BuildArch:     noarch

%description monitoring-aws
AWS Python libraries developed for monitoring OpenShift.

%files monitoring-aws
%{python_sitelib}/openshift_tools/monitoring/awsutil.py
%{python_sitelib}/openshift_tools/monitoring/awsutil.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-monitoring-gcp subpackage
# ----------------------------------------------------------------------------------
%package monitoring-gcp
Summary:       OpenShift Tools GCP Python Libraries Package
Requires:      python2,python-openshift-tools
BuildArch:     noarch

%description monitoring-gcp
GCP Python libraries developed for monitoring OpenShift.

%files monitoring-gcp
%{python_sitelib}/openshift_tools/monitoring/gcputil.py
%{python_sitelib}/openshift_tools/monitoring/gcputil.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-monitoring-openshift subpackage
# ----------------------------------------------------------------------------------
%package monitoring-openshift
Summary:       OpenShift Tools Openshift Python Libraries Package
# and /usr/bin/oc (atomic-openshift-clients or upstream origin-clients)
Requires:      python2,python-openshift-tools,/usr/bin/oc
BuildArch:     noarch

%description monitoring-openshift
Openshift Python libraries developed for monitoring OpenShift.

%files monitoring-openshift
%{python_sitelib}/openshift_tools/monitoring/ocutil.py
%{python_sitelib}/openshift_tools/monitoring/ocutil.py[co]
%{python_sitelib}/openshift_tools/monitoring/oadmutil.py
%{python_sitelib}/openshift_tools/monitoring/oadmutil.py[co]


# ----------------------------------------------------------------------------------
# python-openshift-tools-ansible subpackage
# ----------------------------------------------------------------------------------
%package ansible
Summary:       OpenShift Tools Ansible Python Package
# TODO: once the zbxapi ansible module is packaged, add it here as a dep
Requires:      python2,python-openshift-tools,python-zbxsend,ansible,openshift-tools-ansible-zabbix
BuildArch:     noarch

%description ansible
Tools developed for ansible OpenShift.

%files ansible
%dir %{python_sitelib}/openshift_tools/ansible
%{python_sitelib}/openshift_tools/ansible/*.py
%{python_sitelib}/openshift_tools/ansible/*.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-utils subpackage
# ----------------------------------------------------------------------------------
%package utils
Summary:       OpenShift Tools Utils Python Package
Requires:      python2,python-openshift-tools
BuildArch:     noarch

%description utils
Tools developed for ansible OpenShift.

%files utils
%dir %{python_sitelib}/openshift_tools/utils
%{python_sitelib}/openshift_tools/utils/*.py
%{python_sitelib}/openshift_tools/utils/*.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-web subpackage
# ----------------------------------------------------------------------------------
%package web
Summary:       OpenShift Tools Web Python Package
# python-2.7.5-34 adds native SNI support
Requires:      python2 >= 2.7.5-34
Requires:      python-openshift-tools,python-requests
BuildArch:     noarch

%description web
Tools developed to make it easy to work with web technologies.

# openshift_tools/web files
%files web
%dir %{python_sitelib}/openshift_tools/web
%{python_sitelib}/openshift_tools/web/*.py
%{python_sitelib}/openshift_tools/web/*.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-zbxapi subpackage
# ----------------------------------------------------------------------------------
%package zbxapi
Summary:       OpenShift Tools Zbxapi Python Package
Requires:      python2
BuildArch:     noarch

%description zbxapi
Thin API wrapper to communicate with a Zabbix server

# openshift_tools/zbxapi files
%files zbxapi
%dir %{python_sitelib}/openshift_tools/zbxapi
%{python_sitelib}/openshift_tools/zbxapi/*.py
%{python_sitelib}/openshift_tools/zbxapi/*.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-cloud subpackage
# ----------------------------------------------------------------------------------
%package cloud
Summary:       OpenShift Tools Cloud Python Package
Requires:      python2
BuildArch:     noarch

%description cloud
Adds openshift_tools/cloud python package

# openshift_tools/cloud files
%files cloud
%dir %{python_sitelib}/openshift_tools/cloud
%{python_sitelib}/openshift_tools/cloud/*.py
%{python_sitelib}/openshift_tools/cloud/*.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-cloud-aws subpackage
# ----------------------------------------------------------------------------------
%package cloud-aws
Summary:       OpenShift Tools Aws Cloud Python Package
Requires:      python2,python-openshift-tools-cloud,python-boto
BuildArch:     noarch

%description cloud-aws
Adds Aws specific python modules

# openshift_tools/cloud/aws files
%files cloud-aws
%dir %{python_sitelib}/openshift_tools/cloud/aws
%{python_sitelib}/openshift_tools/cloud/aws/*.py
%{python_sitelib}/openshift_tools/cloud/aws/*.py[co]

# ----------------------------------------------------------------------------------
# python-openshift-tools-cloud-gcp subpackage
# ----------------------------------------------------------------------------------
%package cloud-gcp
Summary:       OpenShift Tools GCP Cloud Python Package
Requires:      python2,python-openshift-tools-cloud,python-boto
BuildArch:     noarch

%description cloud-gcp
Adds GCP specific python modules

# openshift_tools/cloud/gcp files
%files cloud-gcp
%dir %{python_sitelib}/openshift_tools/cloud/gcp
%{python_sitelib}/openshift_tools/cloud/gcp/*.py
%{python_sitelib}/openshift_tools/cloud/gcp/*.py[co]

%changelog
* Wed Jul 17 2019 Matthew Barnes <mbarnes@fedoraproject.org> 0.0.145-1
- simplezabbix: Delete Ansible's tmpdir on TaskQueueManager exception
  (mbarnes@fedoraproject.org)

* Tue Mar 12 2019 Blair Morrison <bmorriso@redhat.com> 0.0.144-1
- Fix format string in ebs_snapshotter library (bmorriso@redhat.com)

* Thu Jan 17 2019 Matt Woodson <mwoodson@redhat.com> 0.0.143-1
- updated the playbook executor code (mwoodson@redhat.com)
- updated sre-bot for new weekend only on call (mail@rafaelazevedo.me)

* Thu Nov 29 2018 Matt Woodson <mwoodson@redhat.com> 0.0.142-1
- changed the version rpm check to look at atomic-openshift-clients
  (mwoodson@redhat.com)

* Tue Oct 30 2018 Matthew Barnes <mbarnes@fedoraproject.org> 0.0.141-1
- inventory_util.py: Make get_cluster() and get_cluster_variable() non-static
  (mbarnes@fedoraproject.org)

* Thu Oct 11 2018 Drew Anderson <dranders@redhat.com> 0.0.140-1
- 

* Mon Oct 01 2018 Kenny Woodson <kwoodson@redhat.com> 0.0.139-1
- updated to fix issues with multiple channels (#3693) (rafael-
  azevedo@users.noreply.github.com)

* Wed Jul 25 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.138-1
- updated SREbot since there was a change on the pagerduty escalation policy
  (#3659) (rafael-azevedo@users.noreply.github.com)
- Another typo (jupierce@redhat.com)
- Comma (jupierce@redhat.com)
- Allowing override of ansible-playbook path (jupierce@redhat.com)
- Remove references of Google Sheets usage (#3613) (will@thegordons.me)
- corrected function call when running update_topic (#3604) (rafael-
  azevedo@users.noreply.github.com)
- Srebot update (#3596) (rafael-azevedo@users.noreply.github.com)
- updated SREBOT to run every 10 minutes instead of every 15 seconds (#3593)
  (rafael-azevedo@users.noreply.github.com)
- Srebot update (#3587) (rafael-azevedo@users.noreply.github.com)

* Thu May 31 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.137-1
- changing logging in snapshot related parts (ihorvath@redhat.com)

* Tue May 29 2018 Matt Woodson <mwoodson@redhat.com> 0.0.136-1
- messing with the version (mwoodson@redhat.com)

* Fri May 25 2018 Matt Woodson <mwoodson@redhat.com> 0.0.135-1
- didn't like the name of oc_get_cmd, renamed it (mwoodson@redhat.com)

* Thu May 24 2018 Matt Woodson <mwoodson@redhat.com> 0.0.134-1
- inventory utils: added a oc_get_md; cleaned up master config
  (mwoodson@redhat.com)

* Wed May 23 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.133-1
- Changed use-tower[12].ops.rhcloud.com and tower.ops.rhcloud.com DNS entries
  to the new bastion centric names. (twiest@redhat.com)

* Mon May 14 2018 Matt Woodson <mwoodson@redhat.com> 0.0.132-1
- Adding vfull back in -- accidentally removed? (jupierce@redhat.com)

* Wed May 09 2018 Matt Woodson <mwoodson@redhat.com> 0.0.131-1
- ansible playbook executor: do verbosity (mwoodson@redhat.com)

* Tue May 08 2018 Matt Woodson <mwoodson@redhat.com> 0.0.130-1
- added verbosity option to ansible playbook executor; added some tools to the
  Cluster class (mwoodson@redhat.com)

* Thu May 03 2018 Matt Woodson <mwoodson@redhat.com> 0.0.129-1
- fixes to the playbook exececutor (mwoodson@redhat.com)

* Tue Apr 17 2018 Matt Woodson <mwoodson@redhat.com> 0.0.128-1
- inventory utils, added vfull version (mwoodson@redhat.com)

* Wed Apr 11 2018 Matt Woodson <mwoodson@redhat.com> 0.0.127-1
- made some unbuffered fixes for the cicd python stuff; added some better
  printing (mwoodson@redhat.com)
- made the playbook executor more verbose (mwoodson@redhat.com)

* Fri Apr 06 2018 Matt Woodson <mwoodson@redhat.com> 0.0.126-1
- added utils to the openshift_tools spec file (mwoodson@redhat.com)

* Fri Apr 06 2018 Matt Woodson <mwoodson@redhat.com> 0.0.125-1
- inventory utils and python libs for python version of cicd-control
  (mwoodson@redhat.com)
- inv utils: made the target code more re-usable (mwoodson@redhat.com)
- moved awsutil -> inventory_util; added cluster class to it
  (mwoodson@redhat.com)

* Tue Mar 06 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.124-1
- ansible api changed, so we must change too (ihorvath@redhat.com)

* Wed Feb 14 2018 Drew Anderson <dranders@redhat.com> 0.0.123-1
- 

* Tue Jan 30 2018 Ivan Horvath <ihorvath@redhat.com> 0.0.122-1
- changing registry for zagg-web (ihorvath@redhat.com)

* Mon Jan 29 2018 Sten Turpin <sten@redhat.com> 0.0.121-1
- srebot: Only warn once per nick when using .all/all: that .msg is a less
  noisy option (wgordon@redhat.com)
- use 'oc adm' instead of deprecated 'oadm' (sedgar@redhat.com)
- /usr/bin/oadm does not exist in OCP 3.8 (sedgar@redhat.com)
- ircbot: allow disabling weekend warnings (wgordon@redhat.com)
- ircbot: localize shift change times instead of using UTC in topic
  (wgordon@redhat.com)
- ircbot: fix bug in calculating shift change times for topic
  (wgordon@redhat.com)
- ircbot: update ordering for shift output (wgordon@redhat.com)
- ircbot: update config to include userserv auth settings (wgordon@redhat.com)
- ircbot: add separate .msg command and update schedules to respect DST
  (wgordon@redhat.com)
- ircbot: do not display shift change info on weekend (wgordon@redhat.com)
- ircbot: move .all-list reply to privmsg (wgordon@redhat.com)
- ircbot: update readme for openshift_sre to include the APIs necessary to
  enable (wgordon@redhat.com)
- fix python3 syntax in trello (aweiteka@redhat.com)
- ircbot: remove separate karma plugin, and provide global config example
  (wgordon@redhat.com)
- add error handling for missing report list move (aweiteka@redhat.com)
- ircbot: add .all announcement and karma (wgordon@redhat.com)
- Fixup pylint (aweiteka@redhat.com)
- Add reporting to trello script (aweiteka@redhat.com)
- ircbot: update weekend notice (wgordon@redhat.com)

* Thu Nov 16 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.120-1
- Add SRE specific ircbot plugin (wgordon@redhat.com)
- catch undefined nick-trello user mapping (aweiteka@redhat.com)
- add karma module (aweiteka@redhat.com)
- clean up trello dir (aweiteka@redhat.com)
- Add trello CLI (aweiteka@redhat.com)

* Wed Nov 08 2017 Thomas Wiest <twiest@redhat.com> 0.0.119-1
- Fixed cron-send-docker-metrics and dockerutil to work with overlayfs.
  (twiest@redhat.com)

* Wed Nov 08 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.118-1
- adding region option to snap creation and trimming (ihorvath@redhat.com)

* Mon Nov 06 2017 Joel Diaz <jdiaz@redhat.com> 0.0.117-1
- limit ebs volume reporting to only cluster volumes (jdiaz@redhat.com)
- trello CLI pylint fixes (aweiteka@redhat.com)
- Add trello CLI (aweiteka@redhat.com)
- SNOW cli tool (aweiteka@redhat.com)

* Fri Oct 27 2017 Kenny Woodson <kwoodson@redhat.com> 0.0.116-1
- adding another exception catch so the execution continues
  (ihorvath@redhat.com)

* Tue Oct 17 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.115-1
- changing how it aws util helper class reads inventory (ihorvath@redhat.com)

* Mon Oct 16 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.114-1
- adding orphaned snapshot delete support (ihorvath@redhat.com)

* Tue Sep 26 2017 Kenny Woodson <kwoodson@redhat.com> 0.0.113-1
- ohi: get node var (mwoodson@redhat.com)

* Tue Sep 26 2017 Kenny Woodson <kwoodson@redhat.com>
- ohi: get node var (mwoodson@redhat.com)

* Mon Sep 11 2017 Kenny Woodson <kwoodson@redhat.com> 0.0.111-1
- made some modifications to ohi and awsutil to accomodate the cluster var
  (mwoodson@redhat.com)
- added a get-env to the ohi utility. defaulted to v3 (mwoodson@redhat.com)

* Fri Apr 28 2017 Thomas Wiest <twiest@redhat.com> 0.0.110-1
- Added cron-send-ec2-ebs-volumes-in-stuck-state.py (twiest@redhat.com)

* Mon Mar 06 2017 Matt Woodson <mwoodson@redhat.com> 0.0.109-1
- 

* Mon Mar 06 2017 Matt Woodson <mwoodson@redhat.com> 0.0.108-1
- 

* Mon Mar 06 2017 Matt Woodson <mwoodson@redhat.com> 0.0.107-1
- config loop tag monitoring work (mwoodson@redhat.com)

* Wed Feb 22 2017 Dan Yocum <dyocum@redhat.com> 0.0.106-1
- 

* Wed Feb 22 2017 Dan Yocum <dyocum@redhat.com> 0.0.105-1
- 

* Mon Feb 20 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.104-1
- Fix typo that cause script failure (zgalor@redhat.com)

* Wed Feb 15 2017 zhiwliu <zhiwliu@redhat.com> 0.0.103-1
- Translate metrics with key "heartbeat.ping" to Hawkular Availability Metrics
  (zgalor@redhat.com)

* Thu Jan 19 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.102-1
- use metric_sender.yaml as default config file for zagg_sender
  (zgalor@redhat.com)
- use metric_sender.yaml as default config file for hawk_sender
  (zgalor@redhat.com)

* Fri Jan 06 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.101-1
- yesterday's fix had an extra letter (ihorvath@redhat.com)

* Thu Jan 05 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.100-1
- fix broken function call (ihorvath@redhat.com)

* Wed Jan 04 2017 Ivan Horvath <ihorvath@redhat.com> 0.0.99-1
- Fix hawk_client to properly send unicode string metrics (zgalor@redhat.com)
- moved to openshift_tools (dyocum@redhat.com)

* Thu Dec 08 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.98-1
- Add tags to metric sender (zgalor@redhat.com)

* Wed Dec 07 2016 Joel Diaz <jdiaz@redhat.com> 0.0.97-1
- Elegant ImportError handling of hawkular-client (zgalor@redhat.com)
- Add MetricSender to monitoring lib (zgalor@redhat.com)
- Add a hawkular configuration, client and sender classes to the monitoring lib
  (kobi.zamir@gmail.com)

* Mon Nov 14 2016 Zhiming Zhang <zhizhang@redhat.com> 0.0.96-1
- add region for the s3 check (zhizhang@zhizhang-laptop-nay.redhat.com)

* Tue Nov 08 2016 Joel Diaz <jdiaz@redhat.com> 0.0.95-1
- router monitoring (jdiaz@redhat.com)

* Tue Oct 25 2016 Drew Anderson <dranders@redhat.com> 0.0.94-1
- 

* Tue Oct 25 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.93-1
- Updating awsutil to handle the refactor. (kwoodson@redhat.com)

* Mon Oct 24 2016 Zhiming Zhang <zhizhang@redhat.com> 0.0.92-1
- 

* Mon Oct 24 2016 Unknown name 0.0.91-1
- pylint missing-docstring (dranders@redhat.com)
- use logger for error display, then raise further (dranders@redhat.com)
- moving up to where the command is setup (dranders@redhat.com)
- enable logger (dranders@redhat.com)
- update for yaml (dranders@redhat.com)
- _run_user_* commands updated (dranders@redhat.com)
- _run_cmd_yaml("get pods") (dranders@redhat.com)
- _run_cmd_yaml("get nodes") (dranders@redhat.com)
- pylint line-too-long (dranders@redhat.com)
- use _run_cmd_yaml (dranders@redhat.com)
- _run_cmd_yaml (dranders@redhat.com)
- _run_cmd gets array join and baseCmd (dranders@redhat.com)
- removing unnecessary variables (dranders@redhat.com)
- fix for get_projects (dranders@redhat.com)

* Mon Oct 24 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.90-1
- Fixed the library call for the multiinventory (kwoodson@redhat.com)

* Mon Oct 24 2016 Wesley Hearn <whearn@redhat.com> 0.0.89-1
- Have _run_cmd handle the namespace (whearn@redhat.com)
- Add logging checks (whearn@redhat.com)

* Sun Oct 23 2016 Unknown name 0.0.88-1
- OCUtil.get_projects() (dranders@redhat.com)
- dry up some awsutil methods. (blentz@redhat.com)

* Tue Oct 11 2016 Wesley Hearn <whearn@redhat.com> 0.0.87-1
- Add openshift metrics checks. Updated ocutil with more features
  (whearn@redhat.com)

* Thu Oct 06 2016 Joel Diaz <jdiaz@redhat.com> 0.0.86-1
- migrate to ansible2 (jdiaz@redhat.com)

* Wed Oct 05 2016 Thomas Wiest <twiest@redhat.com> 0.0.85-1
- Added a sleep between AWS API calls. (twiest@redhat.com)
- Fixed bug in cgrouputil.py where it would throw file not found exceptions
  when the cgroup had gone away. (twiest@redhat.com)

* Mon Sep 26 2016 Sten Turpin <sten@redhat.com> 0.0.84-1
- add python-redis dependency (jdiaz@redhat.com)

* Thu Sep 22 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.83-1
- change ohi/ossh/etc to just use cache by default (jdiaz@redhat.com)

* Thu Sep 22 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.82-1
- zagg uses redis (ihorvath@redhat.com)

* Tue Sep 20 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.81-1
- Added gcs monitoring. (kwoodson@redhat.com)

* Fri Sep 16 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.80-1
- Fixes for labeling, snapshotting, and trimming snapshots.
  (kwoodson@redhat.com)

* Thu Sep 15 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.79-1
- changing the zagg-*-processor scripts to use multiprocessing in hope of
  speedups (ihorvath@redhat.com)

* Thu Sep 15 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.78-1
- Fixing code for snapshots. (kwoodson@redhat.com)

* Mon Sep 12 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.77-1
- Fixed package name. (kwoodson@redhat.com)
- Added cloud-gcp to spec. (kwoodson@redhat.com)

* Mon Sep 12 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.76-1
- Adding gcp snapshot tooling. (kwoodson@redhat.com)

* Mon Sep 12 2016 Thomas Wiest <twiest@redhat.com> 0.0.75-1
- Added cgrouputil.py and changed dockerutil to be able to use it if requested.
  (twiest@redhat.com)

* Thu Sep 08 2016 Ivan Horvath <ihorvath@redhat.com> 0.0.74-1
- adding sharding based on first 2 character to zagg data files
  (ihorvath@redhat.com)
- case issues on multipliers (K/k M/m) (dranders@redhat.com)

* Mon Aug 29 2016 Joel Diaz <jdiaz@redhat.com> 0.0.73-1
- Added cron-send-docker-containers-usage.py (twiest@redhat.com)

* Wed Jul 27 2016 Wesley Hearn <whearn@redhat.com> 0.0.72-1
- Added simple json output to ohi, updated awsutil to have convert_to_ip not
  require a list (whearn@redhat.com)

* Mon Jul 25 2016 Joel Diaz <jdiaz@redhat.com> 0.0.71-1
- add support to ZaggSender to create/send cluster-wide synthetic items
  (jdiaz@redhat.com)
- add --list-cluster to ohi (sten@redhat.com)

* Tue Jun 21 2016 Thomas Wiest <twiest@redhat.com> 0.0.70-1
- Added Name and purpose tagging to ops-ec2-add-snapshot-tag-to-ebs-volumes.py
  (twiest@redhat.com)

* Mon Jun 13 2016 Thomas Wiest <twiest@redhat.com> 0.0.69-1
- Made the snapshot and trim operations more error resistant.
  (twiest@redhat.com)

* Thu Jun 09 2016 Thomas Wiest <twiest@redhat.com> 0.0.68-1
- Changed root device detection to be more accurate. Added volume tag and
  attachment data to snapshot tags. (twiest@redhat.com)

* Wed Jun 08 2016 Thomas Wiest <twiest@redhat.com> 0.0.67-1
- Added more attach names for the root master and node volumes and fixed bug.
  (twiest@redhat.com)

* Wed Jun 08 2016 Thomas Wiest <twiest@redhat.com> 0.0.66-1
- Added ops-ec2-add-snapshot-tag-to-ebs-volumes.py (twiest@redhat.com)

* Wed Jun 01 2016 Sten Turpin <sten@redhat.com> 0.0.65-1
- removed cron-send-build-app, replaced with new capabilities in cron-send-create-app

* Tue May 31 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.64-1
- 

* Fri May 27 2016 Joel Diaz <jdiaz@redhat.com> 0.0.63-1
- memory available and max-mem pod schedulable capacity checks plus new
  'conversions' library and necessary RPM spec updates to include capacity
  checks into monitoring-openshift.rpm (jdiaz@redhat.com)

* Thu May 19 2016 Matt Woodson <mwoodson@redhat.com> 0.0.62-1
- fixed the aws s3 check (mwoodson@redhat.com)

* Wed May 18 2016 Matt Woodson <mwoodson@redhat.com> 0.0.61-1
- added TB to dockerutil (mwoodson@redhat.com)

* Mon May 16 2016 Thomas Wiest <twiest@redhat.com> 0.0.60-1
- Added ops-ec2-snapshot-ebs-volumes.py and ops-ec2-trim-ebs-snapshots.py
  (twiest@redhat.com)

* Fri Apr 22 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.59-1
- Kubeconfig fix (kwoodson@redhat.com)

* Thu Apr 21 2016 Joel Diaz <jdiaz@redhat.com> 0.0.58-1
- depend on ansible1.9 RPM from EPEL (jdiaz@redhat.com)

* Tue Apr 19 2016 Joel Diaz <jdiaz@redhat.com> 0.0.57-1
- push python-2.7.5-34 (SNI) dep into python-openshift-tools-web only
  (jdiaz@redhat.com)

* Tue Apr 19 2016 Joel Diaz <jdiaz@redhat.com> 0.0.56-1
- depend on base python-openshift-tools (for __init__.py) (jdiaz@redhat.com)

* Mon Apr 18 2016 Joel Diaz <jdiaz@redhat.com> 0.0.55-1
- copy host/inventory tools from openshift-ansible/bin and generate equivalent
  RPMs clean up pylint (jdiaz@redhat.com)

* Tue Apr 12 2016 Joel Diaz <jdiaz@redhat.com> 0.0.54-1
- depend on new openshift-tools-ansible-zabbix RPM (jdiaz@redhat.com)

* Tue Mar 15 2016 Joel Diaz <jdiaz@redhat.com> 0.0.53-1
- change deps to binary path requirements (jdiaz@redhat.com)
- add skeleton oadm utility (jdiaz@redhat.com)

* Thu Mar 10 2016 Joel Diaz <jdiaz@redhat.com> 0.0.52-1
- specify minimum python version so we are guaranteed SNI support
  (jdiaz@redhat.com)
- use base python from RHEL for SNI support (jdiaz@redhat.com)

* Thu Mar 10 2016 Joel Diaz <jdiaz@redhat.com> 0.0.51-1
- use base python from RHEL for SNI support (jdiaz@redhat.com)

* Mon Mar 07 2016 Joel Diaz <jdiaz@redhat.com> 0.0.50-1
- python-openshift-tools-ansible needs to pull in openshift-ansible-zabbix this
  allows removal of the embedded libzabbix in the Dockerfile for zagg-web
  container (jdiaz@redhat.com)

* Thu Mar 03 2016 Joel Diaz <jdiaz@redhat.com> 0.0.49-1
- split zbxapi into its own subpackage (jdiaz@redhat.com)

* Thu Mar 03 2016 Joel Diaz <jdiaz@redhat.com> 0.0.48-1
- python-openshift-tools-web package imports python-requests (jdiaz@redhat.com)

* Thu Mar 03 2016 Unknown name 0.0.47-1
- 

* Mon Feb 29 2016 Joel Diaz <jdiaz@redhat.com> 0.0.46-1
- add retry logic and set zagg_client to 2 retries (jdiaz@redhat.com)

* Wed Feb 24 2016 Joel Diaz <jdiaz@redhat.com> 0.0.45-1
- zbxapi import requests. list RPM dependency (jdiaz@redhat.com)

* Wed Feb 17 2016 Joel Diaz <jdiaz@redhat.com> 0.0.44-1
- docker-registry health script (for master and non-master) (jdiaz@redhat.com)

* Tue Feb 09 2016 Sten Turpin <sten@redhat.com> 0.0.43-1
- renamed /etc/openshift to /etc/origin (sten@redhat.com)

* Wed Jan 27 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.42-1
- Updating for latest changes to update hosts (kwoodson@redhat.com)

* Tue Jan 26 2016 Matt Woodson <mwoodson@redhat.com> 0.0.41-1
- supress request ssl warning when ssl verify = false (mwoodson@redhat.com)

* Tue Jan 26 2016 Matt Woodson <mwoodson@redhat.com> 0.0.40-1
- Adding support for master ha checks (kwoodson@redhat.com)

* Thu Jan 21 2016 Thomas Wiest <twiest@redhat.com> 0.0.39-1
- fixed another bug in zabbix_metric_processor.py (twiest@redhat.com)

* Wed Jan 20 2016 Thomas Wiest <twiest@redhat.com> 0.0.38-1
- fixed bug in zabbix_metric_processor.py (twiest@redhat.com)

* Tue Jan 19 2016 Matt Woodson <mwoodson@redhat.com> 0.0.37-1
- separated pcp from zagg sender (mwoodson@redhat.com)

* Mon Jan 18 2016 Matt Woodson <mwoodson@redhat.com> 0.0.36-1
- broke zbxapi into it's own subpackage (mwoodson@redhat.com)
- sepearated openshift-tools rpms into subpackages (mwoodson@redhat.com)

* Wed Dec 16 2015 Thomas Wiest <twiest@redhat.com> 0.0.35-1
- Split ops-zagg-processor.py into ops-zagg-metric-processor.py and ops-zagg-
  heartbeat-processor.py. (twiest@redhat.com)

* Mon Dec 14 2015 Joel Diaz <jdiaz@redhat.com> 0.0.34-1
- Changed ops-zagg-processor to send metrics on the number of metrics in the
  queue, heart beats in the queue and the number of errors while processing.
  (twiest@redhat.com)

* Tue Dec 08 2015 Thomas Wiest <twiest@redhat.com> 0.0.33-1
- Added chunking and error handling to ops-zagg-processor for zabbix targets.
  (twiest@redhat.com)

* Tue Nov 24 2015 Matt Woodson <mwoodson@redhat.com> 0.0.32-1
- changed openshift requires to atomic-openshift (mwoodson@redhat.com)

* Tue Nov 17 2015 Joel Diaz <jdiaz@redhat.com> 0.0.31-1
- Docker cron timing (jdiaz@redhat.com)

* Tue Nov 17 2015 Matt Woodson <mwoodson@redhat.com> 0.0.30-1
- added some updated rest api; added user running pod count
  (mwoodson@redhat.com)
- added the openshift rest api, updated master script (mwoodson@redhat.com)

* Mon Nov 16 2015 Joel Diaz <jdiaz@redhat.com> 0.0.29-1
- Add scripts to report S3 bucket stats from master nodes (jdiaz@redhat.com)

* Tue Nov 03 2015 Matt Woodson <mwoodson@redhat.com> 0.0.28-1
- added the disk tps check (mwoodson@redhat.com)

* Mon Nov 02 2015 Marek Mahut <mmahut@redhat.com> 0.0.27-1
- make sure to share the host's networking with oso-rhel7-zagg-client

* Mon Oct 12 2015 Matt Woodson <mwoodson@redhat.com> 0.0.26-1
- added pcp derived items; added debug and verbose (mwoodson@redhat.com)

* Tue Oct 06 2015 Kenny Woodson <kwoodson@redhat.com> 0.0.25-1
- Adding support for hostgroups (kwoodson@redhat.com)

* Wed Sep 30 2015 Kenny Woodson <kwoodson@redhat.com> 0.0.24-1
- Fix to cron name. Also fix to added parameters for zagg_sender
  (kwoodson@redhat.com)

* Wed Sep 30 2015 Kenny Woodson <kwoodson@redhat.com> 0.0.23-1
- Adding a pcp metric sampler for cpu stats (kwoodson@redhat.com)

* Mon Sep 28 2015 Matt Woodson <mwoodson@redhat.com> 0.0.22-1
- 

* Fri Sep 25 2015 Matt Woodson <mwoodson@redhat.com> 0.0.21-1
- added dynamic prototype support to zagg. added the filsystem checks to use
  this (mwoodson@redhat.com)

* Wed Sep 23 2015 Thomas Wiest <twiest@redhat.com> 0.0.20-1
- added timeout.py (twiest@redhat.com)

* Wed Sep 16 2015 Kenny Woodson <kwoodson@redhat.com> 0.0.19-1
- Convert string to bool for ssl check (kwoodson@redhat.com)

* Wed Sep 16 2015 Unknown name 0.0.18-1
- Adding SSL support for v3 monitoring (kwoodson@redhat.com)
- Adding support for SNI. (kwoodson@redhat.com)

* Tue Aug 18 2015 Matt Woodson <mwoodson@redhat.com> 0.0.17-1
- added discoveryrule (kwoodson@redhat.com)
- Merge pull request #20 from jgkennedy/pr (twiest@users.noreply.github.com)
- Combined the two graphs and refactored some things (jessek@redhat.com)

* Mon Aug 17 2015 Thomas Wiest <twiest@redhat.com> 0.0.16-1
- updated zagg sender to not read defaults (mwoodson@redhat.com)

* Wed Aug 12 2015 Kenny Woodson <kwoodson@redhat.com> 0.0.15-1
- zabbix api library (kwoodson@redhat.com)

* Fri Jul 31 2015 Matt Woodson <mwoodson@redhat.com> 0.0.14-1
- 

* Fri Jul 31 2015 Thomas Wiest <twiest@redhat.com> 0.0.13-1
- added zagg to zagg capability to ops-zagg-processor (twiest@redhat.com)
- added a little more error handling to SimpleZabbix (twiest@redhat.com)

* Wed Jul 15 2015 Thomas Wiest <twiest@redhat.com> 0.0.12-1
- corrected the dependencies of python-openshift-tools-monitoring

* Wed Jul 15 2015 Thomas Wiest <twiest@redhat.com> 0.0.11-1
- added python-openshift-tools-ansible sub package. (twiest@redhat.com)
- changed libs to not be executable (twiest@redhat.com)
- added ops-zagg-processor.py (twiest@redhat.com)
* Tue Jul 07 2015 Thomas Wiest <twiest@redhat.com> 0.0.10-1
- ops-zagg-client (mwoodson@redhat.com)
* Thu Jul 02 2015 Thomas Wiest <twiest@redhat.com> 0.0.9-1
- added heartbeat metric logic to metricmanager (twiest@redhat.com)

* Wed Jul 01 2015 Matt Woodson <mwoodson@redhat.com> 0.0.8-1
- removed test code (mwoodson@redhat.com)
- wrote pcp_to_zagg (mwoodson@redhat.com)

* Thu Jun 25 2015 Matt Woodson <mwoodson@redhat.com> 0.0.7-1
- added basic auth to zagg (mwoodson@redhat.com)

* Thu Jun 25 2015 Thomas Wiest <twiest@redhat.com> 0.0.6-1
- cleaned up zagg_client and rest.py (mwoodson@redhat.com)
- changed python-openshift-tools.spec to have subpackages (twiest@redhat.com)
- separated restapi from zagg_client, removed __init__ from views
  (mwoodson@redhat.com)
- more pylint cleanup (mwoodson@redhat.com)
- pylint fixes (mwoodson@redhat.com)
- initial commit of zagg rest api (mwoodson@redhat.com)
- changed metricmanager to explicitly use zbxsend.Metric (twiest@redhat.com)
- added metricmanager (twiest@redhat.com)
* Thu Jun 25 2015 Thomas Wiest <twiest@redhat.com> 0.0.5-1
- changed python-openshift-tools.spec to have subpackages (twiest@redhat.com)
