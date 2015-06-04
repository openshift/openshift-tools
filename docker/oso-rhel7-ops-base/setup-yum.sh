#!/bin/bash

# The purpose of this script is to setup the yum repo data that is stored in a secret store.
# For now, it just supports docker's /run/secrets/etc-pki-entitlement stuff.
#
# Host secret path: /etc/pki/entitlement/
# Container secret path: /run/secrets/etc-pki-entitlement
#
# Note: Secrets are **COPIED** from the host secret directory to the container secret directory
#       on container build / run. However, they do **NOT** show up in the final container image.


SECRETS_DIR=/run/secrets/etc-pki-entitlement

SAVEIFS=$IFS

# Change IFS so that we can loop over files with spaces in them
IFS=$'\n'

# Link in yum certs
for FILE in ${SECRETS_DIR}/yum/certs/* ; do
    [ -f $FILE ] && ln -sf $FILE /var/lib/yum/$(basename $FILE)
done

echo
ls -la --color /var/lib/yum/
echo

# Link in yum repos
for FILE in ${SECRETS_DIR}/yum/repos/* ; do
    [ -f $FILE ] && ln -sf $FILE /etc/yum.repos.d/$(basename $FILE)
done

echo
ls -la --color /etc/yum.repos.d
echo


# Link in yum gpg keys
for FILE in ${SECRETS_DIR}/yum/rpm-gpg/* ; do
    [ -f $FILE ] && ln -sf $FILE /etc/pki/rpm-gpg/$(basename $FILE)
done

echo
ls -la --color /etc/pki/rpm-gpg
echo

# Set it back to normal
IFS=$SAVEIFS
