#!/bin/bash
#
# This formats and mounts the etcd volume.
#
# The requested device for this volume is /dev/xvdg, but NVMe
# block devices are enumerated as /dev/nvme*n1 and not always
# in the same order as the block device mapping.
#
# Helpfully, Amazon adds the requested device name in the
# vendor-specific portion of the device's embedded data.  We
# extract this data with the nvme(1) utilitiy to determine the
# correct device to format.
#
# See: https://github.com/oogali/ebs-automatic-nvme-mapping

set -e

# See "openshift_aws_master_volumes" in generate_inventory playbook.
ETCD_DEVICE_NAME=xvdg

# Identify empty NVMe volumes using the "file" utility.
# Volumes with no filesystem are described as simply "data".
EMPTY_VOLUMES=$(file --special-files --no-pad /dev/nvme*n* | \
                grep ": data$" | cut --fields=1 --delimiter=':')

for volume in $EMPTY_VOLUMES
do
  # Extract the requested device name from the vendor data
  # portion of the NVMe device.
  VENDOR_DATA=$(nvme id-ctrl --raw-binary "$volume" | cut -c3073-3104 | tr -s ' ' | sed 's/ $//g')
  REQUESTED_DEVICE_NAME="${VENDOR_DATA#/dev/}"

  if [[ "$REQUESTED_DEVICE_NAME" == "$ETCD_DEVICE_NAME" ]]
  then
    pvcreate $volume
    vgcreate etcd $volume
    lvcreate --extents=100%FREE --name etcd etcd
    mkfs.xfs /dev/etcd/etcd
    mkdir --parents /var/lib/etcd
    echo '/dev/mapper/etcd-etcd /var/lib/etcd  xfs  defaults  0 0' >> /etc/fstab
    mount --all
  fi
done
