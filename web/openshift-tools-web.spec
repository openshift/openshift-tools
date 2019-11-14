Summary:       OpenShift Tools Web Services
Name:          openshift-tools-web
Version:       0.0.27
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
mkdir -p %{buildroot}/var/www/zagg
cp -ap zagg %{buildroot}/var/www/

mkdir -p %{buildroot}/etc/httpd/conf.d/
cp -p zagg-httpd.conf %{buildroot}/etc/httpd/conf.d/

# simplesamlphp-modules install
mkdir -p %{buildroot}/usr/share/simplesamlphp/modules
cp -a simplesaml_mods/* %{buildroot}/usr/share/simplesamlphp/modules/


# ----------------------------------------------------------------------------------
# openshift-tools-web-zagg subpackage
# ----------------------------------------------------------------------------------
%package zagg
Summary:       OpenShift Tools Zagg REST API Package
Requires:      python2,python-flask,httpd,python-openshift-tools-monitoring-zagg
BuildRequires: python2-devel
BuildArch:     noarch

%description zagg
OpenShift Tools Zagg REST API

%files zagg
/var/www/zagg
%config(noreplace) /etc/httpd/conf.d/zagg-httpd.conf

# ----------------------------------------------------------------------------------
# openshift-tools-web-simplesamlphp-modules subpackage
# ----------------------------------------------------------------------------------
%package simplesamlphp-modules
Summary:       Auth and theme modules for SimpleSAMLphp
Requires:      php,oso-simplesamlphp
BuildArch:     noarch

%description simplesamlphp-modules
Custom SimpleSAMLphp modules for oso SSO application

%files simplesamlphp-modules
/usr/share/simplesamlphp/modules/*

%changelog
* Tue Nov 12 2019 Matt Woodson <mwoodson@redhat.com> 0.0.27-1
- 

* Tue Nov 12 2019 Matt Woodson <mwoodson@redhat.com>
- 

* Mon Jan 14 2019 Alex Chvatal <achvatal@redhat.com>
- adding dns latency monitoring

* Wed Feb 14 2018 Drew Anderson <dranders@redhat.com> 0.0.24-1
- 

* Wed Sep 27 2017 Dan Yocum <dyocum@redhat.com> 0.0.23-1
-  updated cron-send-metrics-check.py to handle both <3.5 and >3.6 hawkular-passwd locations

* Wed Mar 22 2017 Joel Smith <joesmith@redhat.com> 0.0.22-1
- Make simpleSAML authorizeyaml mod support users in multiple roles
  (joesmith@redhat.com)

* Wed Feb 22 2017 Dan Yocum <dyocum@redhat.com> 0.0.21-1
- 

* Wed Feb 22 2017 Unknown name 0.0.20-1
- 

* Wed Feb 08 2017 Joel Smith <joesmith@redhat.com> 0.0.19-1
- Add optional redirect URL feature to SSO app's authorizeyaml module
  (joesmith@redhat.com)

* Wed Jan 25 2017 Joel Smith <joesmith@redhat.com> 0.0.18-1
- Fix SAML authorization of users in YAML auth module (joesmith@redhat.com)

* Mon Oct 24 2016 Wesley Hearn <whearn@redhat.com> 0.0.17-1
- SSO: move simpleSAML modules to rpm (joesmith@redhat.com)

* Mon Sep 26 2016 Ivan Horvath <ihorvath@redhat.com> 0.0.16-1
- zagg web writes to wrong redis list (ihorvath@redhat.com)

* Thu Sep 22 2016 Kenny Woodson <kwoodson@redhat.com> 0.0.15-1
- zagg uses redis (ihorvath@redhat.com)

* Thu Feb 25 2016 Joel Diaz <jdiaz@redhat.com> 0.0.14-1
- place wsgi socket file in a place we can write to (jdiaz@redhat.com)

* Thu Feb 25 2016 Joel Diaz <jdiaz@redhat.com> 0.0.13-1
- move from django zagg to flask (with apache mpm-worker) (jdiaz@redhat.com)
- Revert "Automatic commit of package [openshift-tools-web] release
  [0.0.12-1]." (sten@redhat.com)
- Automatic commit of package [openshift-tools-web] release [0.0.12-1].
  (sten@redhat.com)

* Thu Feb 25 2016 Joel Diaz <jdiaz@redhat.com>
- move from django zagg to flask (with apache mpm-worker) (jdiaz@redhat.com)
- Revert "Automatic commit of package [openshift-tools-web] release
  [0.0.12-1]." (sten@redhat.com)
- Automatic commit of package [openshift-tools-web] release [0.0.12-1].
  (sten@redhat.com)

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

