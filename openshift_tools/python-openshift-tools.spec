Summary:       OpenShift Tools Python Package
Name:          python-openshift-tools
Version:       0.0.32
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

# openshift_tools/monitoring install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/monitoring
cp -p monitoring/*.py %{buildroot}%{python_sitelib}/openshift_tools/monitoring

# openshift_tools/ansible install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/ansible
cp -p ansible/*.py %{buildroot}%{python_sitelib}/openshift_tools/ansible

# openshift_tools/web install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/web
cp -p web/*.py %{buildroot}%{python_sitelib}/openshift_tools/web


# openshift_tools files
%files
%dir %{python_sitelib}/openshift_tools
%{python_sitelib}/openshift_tools/*.py
%{python_sitelib}/openshift_tools/*.py[co]




# ----------------------------------------------------------------------------------
# python-openshift-tools-monitoring subpackage
# ----------------------------------------------------------------------------------
%package monitoring
Summary:       OpenShift Tools Monitoring Python Package
Requires:      python2,python-openshift-tools,python-zbxsend,python-openshift-tools-web,python-pcp,atomic-openshift,python-awscli
BuildArch:     noarch

%description monitoring
Tools developed for monitoring OpenShift.

%files monitoring
%dir %{python_sitelib}/openshift_tools/monitoring
%{python_sitelib}/openshift_tools/monitoring/*.py
%{python_sitelib}/openshift_tools/monitoring/*.py[co]


# ----------------------------------------------------------------------------------
# python-openshift-tools-ansible subpackage
# ----------------------------------------------------------------------------------
%package ansible
Summary:       OpenShift Tools Ansible Python Package
# TODO: once the zbxapi ansible module is packaged, add it here as a dep
Requires:      python2,python-openshift-tools,python-zbxsend,ansible
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
Requires:      python2,python-openshift-tools
BuildArch:     noarch

%description web
Tools developed to make it easy to work with web technologies.

# openshift_tools/web files
%files web
%dir %{python_sitelib}/openshift_tools/web
%{python_sitelib}/openshift_tools/web/*.py
%{python_sitelib}/openshift_tools/web/*.py[co]


%changelog
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
