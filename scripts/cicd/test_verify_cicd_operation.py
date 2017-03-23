#!/usr/bin/python
import importlib
import unittest

class VerifyCICDOperation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verify = staticmethod(
            importlib.import_module('verify-cicd-operation').verify)

    def test_nothing_allowed(self):
        allowed = []
        f = lambda arg: self.verify(allowed, arg)
        self.assertFalse(f([]))
        self.assertFalse(f(['install']))
        self.assertFalse(f(['install', '--openshift-ansible']))
        self.assertFalse(f(['install', '--openshift-ansible=3.5']))

    def test_one_command(self):
        allowed = [['install']]
        f = lambda arg: self.verify(allowed, arg)
        self.assertTrue(f(['install']))
        self.assertFalse(f([]))
        self.assertFalse(f(['delete']))
        self.assertFalse(f(['upgrade --openshift-ansible=3.5']))

    def test_multiple_commands(self):
        allowed = [['install'], ['delete'], ['update']]
        f = lambda arg: self.verify(allowed, arg)
        self.assertTrue(f(['install']))
        self.assertTrue(f(['delete']))
        self.assertTrue(f(['update']))
        self.assertFalse(f([]))
        self.assertFalse(f(['notallowed']))
        self.assertFalse(f(['notallowed', '--openshift-ansible=3.5']))

    def test_option(self):
        allowed = [['install', '--openshift-ansible=3.5']]
        f = lambda arg: self.verify(allowed, arg)
        self.assertTrue(f(['install', '--openshift-ansible=3.5']))
        self.assertFalse(f([]))
        self.assertFalse(f(['install']))
        self.assertFalse(f(['install', '--openshift-ansible=3.3']))
        self.assertFalse(f(['install', '--something-else=3.5']))
        self.assertFalse(f(['update']))
        self.assertFalse(f(['update', '--something-else=3.5']))

    def test_options(self):
        opt = '--openshift-ansible=3.5'
        allowed = [['install', opt], ['delete', opt], ['update', opt]]
        f = lambda arg: self.verify(allowed, arg)
        self.assertTrue(f(['install', '--openshift-ansible=3.5']))
        self.assertFalse(f([]))
        self.assertFalse(f(['install']))
        self.assertFalse(f(['install', '--openshift-ansible=3.3']))
        self.assertFalse(f(['install', '--something-else=3.5']))
        self.assertFalse(f(['update']))
        self.assertFalse(f(['update', '--something-else=3.5']))

    def test_multiple_commands_options(self):
        allowed = [
            ['install'],
            ['install', '--install-opt'],
            ['delete'],
            ['update', '--update-opt', 'update-arg'],
        ]
        f = lambda arg: self.verify(allowed, arg)
        self.assertTrue(f(['install']))
        self.assertTrue(f(['install', '--install-opt']))
        self.assertTrue(f(['delete']))
        self.assertTrue(f(['update', '--update-opt', 'update-arg']))
        self.assertFalse(f([]))
        self.assertFalse(f(['install', '--update-opt']))
        self.assertFalse(f(['delete', '--install-opt']))
        self.assertFalse(f(['update', '--update-opt']))
        self.assertFalse(f(['update', '--update-opt', 'install-arg']))

    def test_re(self):
        allowed = [
            ['install'],
            ['install', r'--install-opt(=\d+\.\d+)?'],
            ['delete'],
            ['update', '--update-opt', '(update-arg|another-update-arg)'],
        ]
        f = lambda arg: self.verify(allowed, arg)
        self.assertTrue(f(['install', '--install-opt']))
        self.assertTrue(f(['install', '--install-opt=3.5']))
        self.assertTrue(f(['delete']))
        self.assertTrue(f(['update', '--update-opt', 'update-arg']))
        self.assertTrue(f(['update', '--update-opt', 'another-update-arg']))
        self.assertFalse(f([]))
        self.assertFalse(f(['in']))
        self.assertFalse(f(['install', '--install-opt=arg']))
        self.assertFalse(f(['install', '--update-opt']))
        self.assertFalse(f(['delete', '--install-opt']))
        self.assertFalse(f(['update', '--update-opt']))
        self.assertFalse(f(['update', '--update-opt', 'install-arg']))

if __name__ == '__main__':
    unittest.main()
