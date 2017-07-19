openshift_disk_provision
=========

This role creates a partition, creates an LVM volume using that partition, and
creates a filesystem on the new LVM volume.

Requirements
------------

- parted
- mkfs
- lvm2

Role Variables
--------------

odp_volume_name: Name of the disk path

odp_mount_location: Location to mount the created volume

odp_lvm_vg_name: Name of LVM volume group

odp_lvm_lv_name: Name of LVM logical volume

odp_lvm_lvol_size: Volume Size of LVM logical volume

odp_lvm_volume_name: LVM device name. This shouldn't need to be changed.

odp_partition_number: Partition number

odp_partition_name: Name of the partition being created. This shouldn't need to be changed.

odp_filesystem_type: Filesystem type to use for formatting the new partition

Dependencies
------------

Core Modules:
 - filesystem
 - lvol
 - lvg
 - mount
 - parted (new in 2.3, backported into this role's library)


Example Playbook
----------------

        - hosts: localhost
          roles:
            - { role: openshift_disk_provision
                odp_volume_name: "/dev/sda"
                odp_mount_location: "/mnt"
                odp_lvm_vg_name: 'vg'
                odp_lvm_lv_name: 'lv'
                odp_filesystem_type: "ext4"
              }

License
-------

Apache Software License 2.0

Author Information
------------------

OpenShift Operations Team <libra-ops@redhat.com>
