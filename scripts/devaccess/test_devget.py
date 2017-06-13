#!/usr/bin/python

from mock import MagicMock, patch
import os
import sys
import unittest

module_path = os.path.join('/'.join(os.path.realpath(__file__).split('/')[:-1]))
sys.path.insert(0, module_path)

from devaccess_wrap import DevGet, WhitelistedCommands


class DevGetTest(unittest.TestCase):
    def setUp(self):
        DevGet.CONFIG_FILE = './test_devaccess_config.yaml'
        sys.argv = ['devaccess_wrap', 'READ_SSH', 'superperson']
        pass

    def test_unsupported_command(self):
        os.environ['SSH_ORIGINAL_COMMAND'] = '/usr/bin/blah'
        dg = DevGet()
        with self.assertRaises(SystemExit) as cm:
            dg.main()

        self.assertEqual(cm.exception.code, 1)

    def test_oc_get_nodes(self):
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
        myfunc = MagicMock()
        myfunc.side_effect = [node_list]
        with patch.dict(dg._command_dict, {'oc get nodes -ndefault': myfunc}) as mocked:
            dg.main()
            assert myfunc.called

    def test_oc_get_nodes_json(self):
        os.environ['SSH_ORIGINAL_COMMAND'] = 'oc get nodes -ndefault'
        dg = DevGet()
        myfunc = MagicMock()
        myfunc.side_effect = ['json list of nodes']
        with patch.dict(dg._command_dict, {'oc get nodes -ndefault': myfunc}) as mocked:
            dg.main()
            assert myfunc.called

    def test_group_command_uname(self):
        ''' test superperson membership in super_role (which allows 'uname') '''
        os.environ['SSH_ORIGINAL_COMMAND'] = 'uname'
        dg = DevGet()
        myfunc = MagicMock()
        myfunc.side_effect = ['Linux 4.x']
        with patch.dict(dg._command_dict, {'uname': myfunc}) as mocked:
            dg.main()
            assert myfunc.called

if __name__ == '__main__':
    unittest.main()
