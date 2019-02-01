#!/usr/bin/python
# vim: expandtab:tabstop=2:shiftwidth=2
import boto3
from botocore.exceptions import ClientError
# Ansible modules need this wildcard import
# pylint: disable=unused-wildcard-import, wildcard-import, redefined-builtin
from ansible.module_utils.basic import *

''' oo_ec2_elb_set_cert module
    .
Test Playbook:
---
- hosts: localhost
  gather_facts: no
  tasks:
  - include_role:
      name: ../../roles/lib_utils
    static: true

  - oo_ec2_elb_set_cert:
      external_elb_name: 'elb-name'
      aws_iam_openshift_cert_arn: 'certificate id'
      region: "us-east-1"
'''

class AwsElb(object):
    ''' AWS ELB class '''
    def __init__(self):
        self.module = None
        self.elb_client = None
        
    def get_ssl_cert_arn(self, elb_name):
        elb_client = boto3.client('elb')
        try: 
            elb = elb_client.describe_load_balancers(LoadBalancerNames=[elb_name])
        except ClientError as e: 
                self.module.fail_json(failed=True,
                                      msg=e)            

        for listener in elb['LoadBalancerDescriptions'][0]['ListenerDescriptions']:
            if 'SSLCertificateId' in listener['Listener']:
                return listener['Listener']['SSLCertificateId']  

    def set_elb_ssl_cert(self, elb_name, cert_id):
        try:
            response = self.elb_client.set_load_balancer_listener_ssl_certificate(LoadBalancerPort=443, 
            SSLCertificateId=cert_id,
            LoadBalancerName=elb_name)
        except ClientError as e:
                code = e.response['Error']['Code']
                msg = e.response['Error']['Code']
                self.module.fail_json(failed=True, 
                                      msg='AWS API error (%s) occured in ec2_elb_set_cert ansilbe module\n %s\n' %(code, msg))

        return response

    def main(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                external_elb_name=dict(required=True, type='str'),
                aws_iam_openshift_cert_arn=dict(required=True, type='str'),
                region=dict(default=None, required=True, type='str'),
                aws_access_key_id=dict(default=None, type='str'),
                aws_secret_access_key=dict(default=None, type='str'),
            ),
        )

        aws_access_key_id = self.module.params.get('aws_access_key_id')
        aws_secret_access_key = self.module.params.get('aws_secret_access_key')
        external_elb_name = self.module.params.get('external_elb_name')
        SSLCertificateId = self.module.params.get('aws_iam_openshift_cert_arn')

        if aws_access_key_id and aws_secret_access_key:
            boto3.setup_default_session(aws_access_key_id=aws_access_key_id,
                                        aws_secret_access_key=aws_secret_access_key,
                                        region_name=self.module.params['region'])
        else:
            boto3.setup_default_session(region_name=self.module.params['region'])

        self.elb_client = boto3.client('elb')

        if not external_elb_name or not SSLCertificateId:
            self.module.fail_json(failed=True,
                                  msg='external_elb_name or aws_iam_openshift_cert_arn not provided')

        # if cert is already applied exit without errors
        current_cert_id = self.get_ssl_cert_arn(external_elb_name)
        if current_cert_id == SSLCertificateId:
            self.module.exit_json(failed=False, changed=False, msg="SSLCertificateId %s already assigned to load balancer %s" % (SSLCertificateId, external_elb_name))
        
        # set the new cert to the elb 
        respone = self.set_elb_ssl_cert(external_elb_name,SSLCertificateId)
        if respone['ResponseMetadata']['HTTPStatusCode'] != 200:
            self.module.fail_json(failed=True, msg='failed to set elb')
        else:
            current_cert_id = self.get_ssl_cert_arn(external_elb_name)
            if current_cert_id == SSLCertificateId:
                self.module.exit_json(changed=True, result=current_cert_id)
            else:
                self.module.fail_json(failed=True,
                                      msg='failed for unknown reason' )

if __name__ == '__main__':
    AwsElb().main()
