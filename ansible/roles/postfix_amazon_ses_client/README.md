postfix_amazon_ses_client
=========

This configures the postfix to use amazon SES as described here:

http://docs.aws.amazon.com/ses/latest/DeveloperGuide/postfix.html


Requirements
------------

postfxx

Role Variables
--------------

pfases_amazon_ses_server:  amazon ses smtp mail server (provided by AWS)
pfases_amazon_ses_username: amazon ses username (provided by AWS)
pfases_amazon_ses_password: amazon ses password (provided by AWS)

Dependencies
------------

Example Playbook
----------------
  - role: tools_roles/postfix_amazon_ses_client
    pfases_amazon_ses_server: smtp.amazon.example.com
    pfases_amazon_ses_username: username
    pfases_amazon_ses_password: password

License
-------

ASL 2.0

Author Information
------------------

openshift online operations
