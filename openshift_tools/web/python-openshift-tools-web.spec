Summary:       OpenShift Tools Web Python Package
Name:          python-openshift-tools-web
Version:       0.0.1
Release:       1%{?dist}
License:       ASL 2.0
URL:           https://github.com/openshift/openshift-tools
Source0:       %{name}-%{version}.tar.gz
Requires:      python2,python-openshift-tools
BuildRequires: python2-devel
BuildArch:     noarch

%description
Tools developed to make it easy to work with web technologies.

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}%{python_sitelib}/openshift_tools/web

cp -p *.py %{buildroot}%{python_sitelib}/openshift_tools/web/


%files
%{python_sitelib}/openshift_tools/web/

%changelog
* Wed Jun 24 2015 Thomas Wiest <twiest@redhat.com> 0.0.1-1
- new package built with tito

