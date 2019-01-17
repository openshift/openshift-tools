#!/bin/bash
#
# This formats and mounts the etcd volume.
#

set -e

# See "openshift_aws_master_volumes" in generate_inventory playbook.
ETCD_DEVICE_NAME=/dev/xvdc

# A volume with no filesystem is described as simply "data".
FILE_TYPE=$(file --special-files $(realpath $ETCD_DEVICE_NAME) | cut -d' ' -f2-)
if [[ "$FILE_TYPE" == "data" ]]
then
    pvcreate $ETCD_DEVICE_NAME
    vgcreate etcd $ETCD_DEVICE_NAME
    lvcreate --extents=100%FREE --name etcd etcd
    mkfs.xfs /dev/etcd/etcd
    mkdir --parents /var/lib/etcd
    echo '/dev/mapper/etcd-etcd /var/lib/etcd  xfs  defaults  0 0' >> /etc/fstab
    mount --all
fi

