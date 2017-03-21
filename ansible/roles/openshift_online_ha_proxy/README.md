Role Name
=========

Configure the OpenShift Online haproxy: https://github.com/openshift/ops-sop/blob/master/V3/Setup/Online.asciidoc#configure-ose-haproxy-router

Requirements
------------

Role Variables
--------------

Dependencies
------------


Example Playbook
----------------

    - hosts: servers
      roles:
         - tools_roles/openshift_online_ha_proxy

License
-------

Apache 2.0

Author Information
------------------

OpenShift Operations Team
