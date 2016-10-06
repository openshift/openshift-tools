#!/bin/bash

# This install script runs during a docker build to create a minimal
# simleSAMLphp installation. It was created as a part of the project
# at https://github.com/openshift/openshift-tools/tree/prod/docker/oso-saml-sso

# any error should cause this script to exit with an error
set -e -o pipefail

# download and unpack the tarball
wget --quiet -O - 'https://github.com/simplesamlphp/simplesamlphp/releases/download/v1.14.8/simplesamlphp-1.14.8.tar.gz' | \
        tar -x -z -C '/usr/share/' -f -

# strip the version number for the dir name
mv /usr/share/simplesamlphp-* /usr/share/simplesamlphp

# we provide our own config
rm -rf /usr/share/simplesamlphp/config/*
# and we want it also accessible as /etc/simplesamlphp
ln -sf /usr/share/simplesamlphp/config /etc/simplesamlphp

# we provide our own metadata
rm -rf /usr/share/simplesamlphp/metadata
mkdir /etc/simplesamlphp/metadata
ln -sf /etc/simplesamlphp/metadata /usr/share/simplesamlphp/metadata

# this makes it so the simplsaml application is reachable through apache httpd
ln -sf /usr/share/simplesamlphp/www /var/www/html/saml

# this is where we'll be logging
mkdir /var/log/simplesaml

# security hardening. first, remove unneeded PHP scripts reachable via the web server
# so that any undiscovered vulns that may be in them won't bite us
rm -rf /usr/share/simplesamlphp/www/{shib13,admin,index.php,errorreport.php}
rm -f /usr/share/simplesamlphp/www/saml2/idp/{ArtifactResolutionService,initSLO,metadata,SingleLogoutService}.php
# that should leave the following required PHP files:
# www/saml2/idp/SSOService.php
# www/_include.php
# www/logout.php
# www/module.php

# next, disable modules that we're not using so that any undiscovered vulns that may
# be in them won't bite us
touch /usr/share/simplesamlphp/modules/{ldap,sqlauth,portal,multiauth,sanitycheck,consent}/disable
# that should leave only the following enabled:
# authgoogle
# authorize
# authorizeyaml
# saml
# themeoso


# make sure that we have an index in each directory off of www
# so that it automatically redirects to the service list if somebody
# goes to one of the directories directly
for dir in /usr/share/simplesamlphp/www/{,saml2/{,idp/}}; do
   ln -sf /var/www/html/index.php "$dir"
done
