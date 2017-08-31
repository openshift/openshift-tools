openshift_aws_group
=========

Ansible role for creating IAM groups in AWS

Requirements
------------

Ansible Modules:


Role Variables
--------------

- `osasso_account_number`: The AWS account number of the account to operate on (should match the AWS credentials in scope)
- `osasso_roles`: A list of 0 or more roles in the following format:

```
  - role: rolename
    policies:
      - iam_policy_name: policy_name
        iam_json_policy: policy_document
      ...
  ...
```

See http://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html for
information about how to create a policy document.

- `osasso_tech_contact_email`: The contact email address to be added to the SAML metadata document
- `osasso_idp_name`: The name (identifier) for the SAML IdP
- `osasso_idp_hostname`: The hostname of the SAML IdP
- `osasso_idp_certificate`: The X.509 certificate of the SAML IdP. It should be base64-encoded, but should not have any header or footer.
- `osasso_tech_contact_name`: The given name(s) of the IdP administrator (contact person) to be added to the metadata document.
- `osasso_tech_contact_surname`: The surname of the IdP administrator (contact person) to be added to the metadata document.


Dependencies
------------


Example Playbook
----------------

The example shows 2 roles being passed in (one with 1 policy, one with 2), but
in many setups, only 1 role with one policy would be passed in.

```
  - role: tools_roles/openshift_aws_iam_sso
    osasso_account_number: 123456789012
    osasso_idp_name: my_idp
    osasso_idp_hostname: sso.example.com
    # The XML document needs the certificate header and footer stripped off, and all whitespace removed
    osasso_idp_certificate: "{{ pem_cert_data.split('\n') | join('') | regex_replace('-----(?:BEGIN|END) CERTIFICATE-----', '') }}"
    osasso_tech_contact_email: sso_admin@example.com
    osasso_tech_contact_name: John
    osasso_tech_contact_surname: Doe
    osasso_roles:
    - role: admin
      policies:
        - iam_policy_name: AdministratorAccess
          iam_json_policy: |
            {
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Effect": "Allow",
                  "Action": "*",
                  "Resource": "*"
                }
              ]
            }
    - role: cred_test
      policies:
        - iam_policy_name: GetRoleAccess
          iam_json_policy: |
            {
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Effect": "Allow",
                  "Action": [
                    "iam:GetRole"
                  ],
                  "Resource": [
                    "arn:aws:iam::123456789012:role/cred_test"
                  ]
                }
              ]
            }
        - iam_policy_name: GetSAMLProviderAccess
          iam_json_policy: |
            {
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Effect": "Allow",
                  "Action": [
                    "iam:GetSAMLProvider"
                  ],
                  "Resource": [
                    "arn:aws:iam::123456789012:saml-provider/my_idp"
                  ]
                }
              ]
            }

```

License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
