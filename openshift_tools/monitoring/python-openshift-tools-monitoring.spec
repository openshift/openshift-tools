Summary:       OpenShift Tools Monitoring Python Package
Name:          python-openshift-tools-monitoring
Version:       0.0.2
Release:       1%{?dist}
License:       ASL 2.0
URL:           https://github.com/openshift/openshift-tools
Source0:       %{name}-%{version}.tar.gz
Requires:      python2,python-openshift-tools,python-zbxsend
BuildRequires: python2-devel
BuildArch:     noarch

%description
Tools developed for monitoring OpenShift.

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/monitoring

cp -p *.py %{buildroot}%{python_sitelib}/openshift_tools/monitoring/


%files
%{python_sitelib}/openshift_tools/monitoring/

%changelog
* Mon Jun 15 2015 Thomas Wiest <twiest@redhat.com> 0.0.2-1
- added metricmanager (twiest@redhat.com)

* Wed Jun 10 2015 Thomas Wiest <twiest@redhat.com> 0.0.1-1
- new package built with tito

