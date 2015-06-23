# TODO: make openshift-tools-web-zagg a subpackage of openshift-tools-web!!!
#       Without that, we can have only 1 package from this directory (tito design)

Summary:       OpenShift Tools Zagg REST API Package
Name:          openshift-tools-web-zagg
Version:       0.0.0
Release:       1%{?dist}
License:       ASL 2.0
URL:           https://github.com/openshift/openshift-tools
Source0:       %{name}-%{version}.tar.gz
Requires:      python2,python-django,httpd
BuildRequires: python2-devel
BuildArch:     noarch

%description
Zagg REST API

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/opt/zagg
cp -ap zagg %{buildroot}/opt/zagg/

mkdir -p %{buildroot}/etc/httpd/conf.d/
cp -p zagg-httpd.conf %{buildroot}/etc/httpd/conf.d/

%files
/opt/zagg/
%config(noreplace) /etc/httpd/conf.d/*.conf

%changelog
