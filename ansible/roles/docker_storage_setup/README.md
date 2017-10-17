docker_storage_setup
====================

This role converts Docker's storage driver to devicemapper or overlay2.

It requires the block device to be already provisioned and attached to the host.

  Notes:
  * This is NOT idempotent. Conversion needs to be done for it to be idempotent.
  * This will remove `/var/lib/docker`!
  * You will need to re-deploy Docker images.

Configure docker_storage_setup
------------------------------

None

Role Variables
--------------

* `dss_docker_device`: defaults to `/dev/xvdb`
* `dss_docker_storage_driver`: `devicemapper` (default) or `overlay2`

When `dss_docker_storage_driver` is `devicemapper`:

* `dss_docker_storage_dm_basesize`: applies to `dm.basesize` storage
  option (defaults to `3G`)

When `dss_docker_storage_driver` is `overlay2`:

* `dss_docker_storage_overlay2_size`: applies to `overlay2.size` storage
   option (defaults to `3G`)

Dependencies
------------

None

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role/docker_storage_setup, dss_docker_device: '/dev/xvdb' }

License
-------

ASL 2.0

Author Information
------------------

OpenShift operations, Red Hat, Inc
