openshift_registry
=========

Ansible role for setting up and configuring a registry in Openshift

Requirements
------------

Ansible Modules:

- tools_roles/lib_openshift_3.2


Role Variables
--------------

osareg_aws_access_key: aws key that the registry will use for the S3 backend
osareg_aws_secret_key: aws secret key that the registry will use for the S3 backend
osareg_cacert_content: content of the ca cert of the certficate for the registry (used in the external route)
osareg_openshift_cert_content: content of the cert for the registry (used in the external route)
osareg_openshift_key_content: content of the key needed for the registry (used in the external route)
osareg_clusterid: clusterid.  The generates the domain name
osareg_master_nodes: the master nodes that need to be restarted
osareg_region: region to install the s3 bucket.
osareg_registry_http_secret: secret for the docker registry needed for load balancing
osareg_bucket_name: name of the bucket to store the docker registry
osareg_cred_path: Path to gcp docker creds

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
