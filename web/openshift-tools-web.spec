Summary:       OpenShift Tools Web Services
Name:          openshift-tools-web
Version:       0.0.11
Release:       1%{?dist}
License:       ASL 2.0
URL:           https://github.com/openshift/openshift-tools
Source0:       %{name}-%{version}.tar.gz
BuildArch:     noarch

%description
OpenShift Tools Web Services

%prep
%setup -q

%build

%install

# zagg install
mkdir -p %{buildroot}/opt/rh/zagg
mkdir -p %{buildroot}/var/www/zagg2
cp -ap zagg %{buildroot}/opt/rh/
cp -ap zagg2 %{buildroot}/var/www/

mkdir -p %{buildroot}/etc/httpd/conf.d/
cp -p zagg-httpd.conf %{buildroot}/etc/httpd/conf.d/
cp -p zagg2-httpd.conf %{buildroot}/etc/httpd/conf.d/


# ----------------------------------------------------------------------------------
# openshift-tools-web-zagg subpackage
# ----------------------------------------------------------------------------------
%package zagg
Summary:       OpenShift Tools Zagg REST API Package
Requires:      python2,python-django,httpd
BuildRequires: python2-devel
BuildArch:     noarch

%description zagg
OpenShift Tools Zagg REST API

%files zagg
/opt/rh/zagg/
%config(noreplace) /etc/httpd/conf.d/zagg-httpd.conf

# ----------------------------------------------------------------------------------
# openshift-tools-web-zagg2 subpackage
# ----------------------------------------------------------------------------------
%package zagg2
Summary:       OpenShift Tools Zagg2 REST API Package
Requires:      python2,python-flask,httpd,python-openshift-tools-monitoring-zagg
BuildRequires: python2-devel
BuildArch:     noarch

%description zagg2
OpenShift Tools Zagg2 REST API

%files zagg2
/var/www/zagg2
%config(noreplace) /etc/httpd/conf.d/zagg2-httpd.conf

%changelog
* Wed Jan 27 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.11-1
- Revert "Automatic commit of package [openshift-tools-web] release
  [0.0.11-1]." (gburges@use-ctl1.ops.rhcloud.com)
- Automatic commit of package [openshift-tools-web] release [0.0.11-1].
  (gburges@use-ctl1.ops.rhcloud.com)

* Wed Sep 30 2015 Kenny Woodson <kwoodson@redhat.com> 0.0.10-1
- 

* Wed Sep 16 2015 Kenny Woodson <kwoodson@redhat.com> 0.0.9-1
- Adding SNI support for v3 monitoring

* Fri Jul 31 2015 Matt Woodson <mwoodson@redhat.com> 0.0.8-1
- stupid pylint (mwoodson@redhat.com)
- cleaned up settigns.py for zagg (mwoodson@redhat.com)
- added error_log output to zagg web (mwoodson@redhat.com)
- Removed htpasswd as we're now generating it on container startup. Changed
  build.sh scripts to display the time it took to build the image.
  (twiest@redhat.com)

* Wed Jul 15 2015 Thomas Wiest <twiest@redhat.com> 0.0.7-1
- added config file support to zagg-web (twiest@redhat.com)

* Thu Jun 25 2015 Matt Woodson <mwoodson@redhat.com> 0.0.6-1
- added the allowed hosts to everywhere (mwoodson@redhat.com)

* Thu Jun 25 2015 Matt Woodson <mwoodson@redhat.com> 0.0.5-1
- added basic auth to zagg (mwoodson@redhat.com)

* Thu Jun 25 2015 Thomas Wiest <twiest@redhat.com> 0.0.4-1
- new package built with tito

