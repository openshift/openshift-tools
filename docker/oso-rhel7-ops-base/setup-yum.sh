#!/bin/bash -e

# The purpose of this script is to setup the yum repo data that is stored in a secret store.
# For now, it just supports docker's /run/secrets/etc-pki-entitlement stuff.
#
# Host secret path: /etc/pki/entitlement/
# Container secret path: /run/secrets/etc-pki-entitlement
#
# Note: Secrets are **COPIED** from the host secret directory to the container secret directory
#       on container build / run. However, they do **NOT** show up in the final container image.

function create_symlink()
{
    SRC=$1
    DEST=$2

    if [ -f $SRC ] ; then
        echo "  Setting up symlink: $DEST -> $SRC"
        ln -sf $SRC $DEST
    fi
}

echo
echo

SECRETS_DIR=/run/secrets/etc-pki-entitlement

SAVEIFS=$IFS

# Change IFS so that we can loop over files with spaces in them
IFS=$'\n'

# Link in yum certs
for FILE in ${SECRETS_DIR}/yum/certs/* ; do
    DEST="/var/lib/yum/$(basename $FILE)"
    create_symlink "$FILE" "$DEST"
done

# Link in yum repos
for FILE in ${SECRETS_DIR}/yum/repos/* ; do
    DEST="/etc/yum.repos.d/$(basename $FILE)"
    create_symlink "$FILE" "$DEST"
done

# Link in yum gpg keys
for FILE in ${SECRETS_DIR}/yum/rpm-gpg/* ; do
    DEST="/etc/pki/rpm-gpg/$(basename $FILE)"
    create_symlink "$FILE" "$DEST"
done

# Set it back to normal
IFS=$SAVEIFS

echo
echo
