Summary:       OpenShift Tools Python Package
Name:          python-openshift-tools
Version:       0.0.1
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
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools

cp -p *.py %{buildroot}%{python_sitelib}/openshift_tools/


%files
%{python_sitelib}/openshift_tools/

%changelog
* Wed Jun 10 2015 Thomas Wiest <twiest@redhat.com> 0.0.1-1
- new package built with tito

