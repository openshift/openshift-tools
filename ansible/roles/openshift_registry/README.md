openshift_registry
=========

Ansible role for setting up and configuring a registry in Openshift

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2


Role Variables
--------------

osreg_aws_access_key: aws key that the registry will use for the S3 backend
osreg_aws_secret_key: aws secret key that the registry will use for the S3 backend
osreg_cacert_content: content of the ca cert of the certficate for the registry (used in the external route)
osreg_openshift_cert_content: content of the cert for the registry (used in the external route)
osreg_openshift_key_content: content of the key needed for the registry (used in the external route)
osreg_clusterid: clusterid.  The generates the domain name
osreg_master_nodes: the master nodes that need to be restarted
osreg_region: region to install the s3 bucket.
osreg_registry_http_secret: secret for the docker registry needed for load balancing
osreg_bucket_name: name of the bucket to store the docker registry
osreg_cred_path: Path to gcp docker creds

Dependencies
------------


Example Playbook
----------------


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
