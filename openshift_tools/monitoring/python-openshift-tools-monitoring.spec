Summary:       OpenShift Tools Monitoring Python Package
Name:          python-openshift-tools-monitoring
Version:       0.0.0
Release:       1%{?dist}
License:       ASL 2.0
URL:           https://github.com/openshift/openshift-tools
Source0:       %{name}-%{version}.tar.gz
Requires:      python2,python-openshift-tools
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
