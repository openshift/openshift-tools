lib_aws_service_limit
=========

This module exposes AWS service limits and account attributes as Ansible
facts.

The module creates two facts: "aws_service_limits" and "aws_account_attributes"

Account attributes are retrieved via the DescribeAccountAttributes() API call,
which is documented here:
https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeAccountAttributes.html

Service Limits are retrieved via the Trusted Advisor
DescribeTrustedAdvisorCheckResult() API call, which is documented here:
https://docs.aws.amazon.com/awssupport/latest/APIReference/API_DescribeTrustedAdvisorCheckResult.html

NOTE: The information provided by Trusted Advisor must be periodically
refreshed. Refreshing this information is outside the scope of this module.
Failure to schedule periodic refreshes may result in this module reporting
stale information that does not accurately reflect your current usage.

Requirements
------------

boto 3.x+

Module Variables
--------------

region:  String - The AWS region that boto should use for creating the AWS connection.

Dependencies
------------

None

Example Playbook
----------------

- name: include service limits role
  include_role:
    name: lib_aws_service_limit

- name: load service limits module
  aws_service_limit:
    region: 'us-east-1'

Example Output
----------------

"aws_service_limits": [
    {
        "current_value": integer,
        "limit_name": string,
        "limit_value": integer,
        "region": string,
        "service": string,
        "status": string
    },
]

"aws_account_attributes": {
    "default-vpc": string,
    "max-elastic-ips": integer,
    "max-instances": integer,
    "supported-platforms": string,
    "vpc-max-elastic-ips": integer,
    "vpc-max-security-groups-per-interface": integer 
}


License
-------

Apache Software License 2.0

Author Information
------------------

Brett Lentz <blentz@redhat.com>
