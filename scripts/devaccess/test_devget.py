#!/usr/bin/python

''' Tests for devaccess_wrap.py tool '''

# Removing invalid variable names for tests so that I can
# keep them brief
# pylint: disable=invalid-name

# Allow modifying internal structures for mocking
# pylint: disable=protected-access

# 'mock' not available in jenkins environment
# pylint: disable=import-error

# disable unused variables since we sometimes only need to
# initiate the variable to perform the test
# pylint: disable=unused-variable

import os
import sys
import unittest
from mock import MagicMock, mock, patch

module_path = os.path.join('/'.join(os.path.realpath(__file__).split('/')[:-1]))
sys.path.insert(0, module_path)

# Need to set module path (using oc.*) before trying to
# import devaccess_wrap
# pylint: disable=wrong-import-position
from devaccess_wrap import DevGet, DevGetError

class DevGetTest(unittest.TestCase):
    ''' unittest class for testing devaccess_wrap.py '''

    # No 'self' use is intended here
    # pylint: disable=no-self-use
    def setUp(self):
        ''' steps to run before every test run '''
        DevGet.CONFIG_FILE = './test_devaccess_config.yaml'
        sys.argv = ['devaccess_wrap', 'READ_SSH', 'nobody']

    def test_unsupported_command(self):
        ''' Test trying to run a command that isn't supported '''
        os.environ['SSH_ORIGINAL_COMMAND'] = '/usr/bin/blah'
        dg = DevGet()
        with self.assertRaises(SystemExit) as cm:
            dg.main()

        self.assertEqual(cm.exception.code, 1)

    @mock.patch('devaccess_wrap.WhitelistedCommands.oc_get_nodes')
    def test_oc_get_nodes(self, mock_get_nodes):
        ''' Test running 'oc get nodes (allowed) '''
        node_list = '''NAME                            STATUS                     AGE
ip-172-31-49-119.ec2.internal   Ready,SchedulingDisabled   45d
ip-172-31-49-14.ec2.internal    Ready,SchedulingDisabled   45d
ip-172-31-49-245.ec2.internal   Ready,SchedulingDisabled   45d
ip-172-31-50-220.ec2.internal   Ready                      45d
ip-172-31-52-126.ec2.internal   Ready,SchedulingDisabled   45d
ip-172-31-55-174.ec2.internal   Ready,SchedulingDisabled   45d
ip-172-31-56-150.ec2.internal   Ready,SchedulingDisabled   45d
ip-172-31-57-154.ec2.internal   Ready,SchedulingDisabled   45d
ip-172-31-58-0.ec2.internal     Ready                      45d
ip-172-31-60-174.ec2.internal   Ready                      45d
ip-172-31-60-254.ec2.internal   Ready,SchedulingDisabled   45d
ip-172-31-61-118.ec2.internal   Ready                      45d
ip-172-31-61-149.ec2.internal   Ready                      45d
ip-172-31-61-94.ec2.internal    Ready                      45d
ip-172-31-62-44.ec2.internal    Ready,SchedulingDisabled   45d
'''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc get nodes'
        dg = DevGet()
        mock_get_nodes.side_effect = [node_list]

        dg.main()
        assert mock_get_nodes.called

    @mock.patch('devaccess_wrap.WhitelistedCommands.oc_get_nodes')
    def test_oc_get_nodes_json(self, mock_get_nodes):
        ''' Test running oc get nodes -ojson (supported) '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc get nodes -ndefault'
        dg = DevGet()
        mock_get_nodes.side_effect = ['json list of nodes ']

        dg.main()
        assert mock_get_nodes.called


    def test_group_command_uname(self):
        ''' Test superperson membership in super_role (which allows 'uname') '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'uname'
        dg = DevGet()
        myfunc = MagicMock()
        myfunc.side_effect = ['Linux 4.x']
        with patch.dict(dg._command_dict, {'uname': myfunc}):
            dg.main()
            assert myfunc.called

    def test_leading_dash_parameters(self):
        ''' Test oc -n -n (next token has leading '-') '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc -n -n'
        with self.assertRaises(DevGetError):
            dg = DevGet()

    def test_leading_dash_param_single_token(self):
        ''' Test oc -n-blah (leading '-' as value of param) '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc -n-blah'
        with self.assertRaises(DevGetError):
            dg = DevGet()

    def test_param_without_value(self):
        ''' Test oc get pods -n (no actual namespace) '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc get pods -n'
        with self.assertRaises(DevGetError):
            dg = DevGet()

        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc logs pod -c'
        with self.assertRaises(DevGetError):
            dg = DevGet()

        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc get pods -o'
        with self.assertRaises(DevGetError):
            dg = DevGet()

    def test_params_with_same_value(self):
        ''' Test oc get pods -n test -o test (different params with same value) '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc get pods -n test -o test'
        dg = DevGet()
        assert dg._oc_cmd.normalized_cmd() == 'oc get pods -ntest -otest'

    def test_invalid_param_value(self):
        ''' Test oc get pods -n-test '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc get pods -n-test'
        with self.assertRaises(DevGetError):
            dg = DevGet()

        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc get pods -ntest-'
        with self.assertRaises(DevGetError):
            dg = DevGet()

    def test_invalid_username(self):
        ''' Test invalid user name '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'test command'
        sys.argv = ['devaccess_wrap.py', 'READ_SSH', 'inval$d']
        with self.assertRaises(DevGetError):
            dg = DevGet()

    @mock.patch('devaccess_wrap.WhitelistedCommands.rpm_qa')
    def test_user_with_no_defined_roles(self, mock_rpm_qa):
        ''' Test user with no defined roles (ie only default role membership) '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'rpm -qa'
        sys.argv = ['devaccess_wrap.py', 'READ_SSH', 'noroleuser']
        dg = DevGet()

        mock_rpm_qa.side_effect = ['rpm-4.13.0.1-1.fc25.x86_64']
        dg.main()
        assert mock_rpm_qa.called

if __name__ == '__main__':
    unittest.main()
