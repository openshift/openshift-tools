# TODO: make openshift-tools-web-zagg a subpackage of openshift-tools-web!!!
#       Without that, we can have only 1 package from this directory (tito design)

Summary:       OpenShift Tools Zagg REST API Package
Name:          openshift-tools-web-zagg
Version:       0.0.3
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
mkdir -p %{buildroot}/opt/rh/zagg
cp -ap zagg %{buildroot}/opt/rh/

mkdir -p %{buildroot}/etc/httpd/conf.d/
cp -p zagg-httpd.conf %{buildroot}/etc/httpd/conf.d/

%files
/opt/rh/zagg/
%config(noreplace) /etc/httpd/conf.d/*.conf

%changelog
* Wed Jun 24 2015 Thomas Wiest <twiest@redhat.com> 0.0.3-1
- changed /opt/zagg to /opt/rh/zagg to comply with FHS (twiest@redhat.com)
- separated restapi from zagg_client, removed __init__ from views
  (mwoodson@redhat.com)

* Tue Jun 23 2015 Thomas Wiest <twiest@redhat.com> 0.0.2-1
- put in bullshit call (mwoodson@redhat.com)
- fixed pathing for openshift-tools-web-zagg.spec (twiest@redhat.com)
- fixed the metricmanager namespace (mwoodson@redhat.com)

* Tue Jun 23 2015 Thomas Wiest <twiest@redhat.com> 0.0.1-1
- new package built with tito

