Summary:       OpenShift Tools Python Package
Name:          python-openshift-tools
Version:       0.0.80
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
Requires:      python2,python-openshift-tools,python-openshift-tools-web,python-zbxsend
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
# Requiring on /usr/bin/oadm (atomic-openshift or upstream origin
# and /usr/bin/oc (atomic-openshift-clients or upstream origin-clients)
Requires:      python2,python-openshift-tools,/usr/bin/oadm,/usr/bin/oc
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
Requires:      python2,python-openshift-tools,python-zbxsend,ansible1.9,openshift-tools-ansible-zabbix
BuildArch:     noarch

%description ansible
Tools developed for ansible OpenShift.

%files ansible
%dir %{python_sitelib}/openshift_tools/ansible
%{python_sitelib}/openshift_tools/ansible/*.py
%{python_sitelib}/openshift_tools/ansible/*.py[co]


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
