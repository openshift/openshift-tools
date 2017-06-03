#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
See Ansible Module Documentation (Below)
'''

DOCUMENTATION = '''
---
module: iptables_chain
short_description: Entirely manage a single iptables chain
description:
     - Set the rules of a chain to match the specified rules.
options:
  name:
    description:
      - Name of iptables chain
    required: true
  table:
    description:
      - One of filter, nat, mangle, raw, security. The table where the chain should exist.
    required: false
    default: filter
  ip_version:
    description:
      - One of ipv4, ipv6. The IP version that the chain applies to.
    required: false
    default: ipv4
  rules:
    description:
      - |-
        A list of iptables rules which the chain should match. The list
        should be derived from the 'iptables -S <chain>' command so that
        the rules will match later rule dumps on re-runs. Otherwise, the
        module will give the following error:
          Chain update failed. Do input rules match 'iptables -S your_chain' output?
        The easiest way to make sure that rules match is to create a chain
        once manually, then to dump with 'iptables -S <chain>'. Note: the rules
        should not contain a '-N <chain>' rule.

    required: true
author:
    - "Joel Smith (joelsmith@redhat.com)"
'''

EXAMPLES = '''
# Basic iptables chain example
tasks:
- name: Create the example chain
  iptables_chain:
    name: example
    rules:
        - "-A example -p udp -m udp --dport 1025:65535 -m conntrack --ctstate NEW -j ACCEPT"
        - "-A example -p tcp -m tcp --dport 1025:65535 -m conntrack --ctstate NEW -j ACCEPT"
        - "-A example -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT"
        - "-A example -p udp -m udp --dport 137 -m conntrack --ctstate NEW -j ACCEPT"
        - "-A example -p udp -m udp --dport 138 -m conntrack --ctstate NEW -j ACCEPT"
'''

import os
import subprocess
import fcntl
import errno
import time

class IpTablesChainError(Exception):
    '''All IpTablesChain methods throw this exception when errors occur'''
    def __init__(self, msg, cmd, exit_code, output):
        super(IpTablesChainError, self).__init__(msg)
        self.msg = msg
        self.cmd = cmd
        self.exit_code = exit_code
        self.output = output

# pylint: disable=too-few-public-methods
# as seen on http://stackoverflow.com/questions/27803059/conditional-with-statement-in-python
class DummyContextMgr(object):
    '''A dummy context manager that does nothing so that a 'with' can conditionally do nothing'''
    def __enter__(self):
        return None
    def __exit__(self, exc_type, exc_value, traceback_):
        return False
# pylint: enable=too-few-public-methods

class IpTablesChain(object):
    '''A single chain to be managed entirely'''

    def __init__(self, table, iptchain, ver):
        '''Create a single chain manager'''
        self.table = table
        self.chain = iptchain
        self.ver = ver
        self.restore_has_locks = None  # i.e., unknown
        self.wait_takes_seconds = None  # i.e., unknown

    def _build_cmd(self, *args):
        '''
        Create an iptables or ip6tables command
        Return a list of command args suitable for use with subprocess.*
        '''
        cmd = 'iptables' if self.ver == 'ipv4' else 'ip6tables'
        retval = ["/usr/sbin/%s" % cmd, '--table', self.table]

        retval.append('--wait')
        if self._check_wait_takes_seconds():
            retval.append('600')
        retval.extend(args)
        return retval

    def _build_restore_cmd(self, *args):
        '''
        Create an iptables-restore or ip6tables-restore command
        Return a list of command args suitable for use with subprocess.*
        '''
        cmd = 'iptables-restore' if self.ver == 'ipv4' else 'ip6tables-restore'
        retval = ["/usr/sbin/%s" % cmd, '--noflush', '--table', self.table]
        if self._check_restore_has_locks():
            retval.extend(['--wait', '600'])
        retval.extend(args)
        return retval

    def _check_wait_takes_seconds(self):
        '''Determine whether iptables -w accepts an optional timeout'''
        # some versions of iptables have --wait and -w, but don't allow a timeout to be specified
        if self.wait_takes_seconds is None:
            cmd = 'iptables' if self.ver == 'ipv4' else 'ip6tables'
            # try a harmless operation that allows us to see if iptables pukes on the 1
            to_run = ["/usr/sbin/%s" % cmd, '--wait', '10', '--rename-chain', 'INPUT', 'INPUT']
            try:
                subprocess.check_output(to_run, stderr=subprocess.STDOUT)
                # we don't expect to ever get here, but if we do, then I guess it takes seconds.
                self.wait_takes_seconds = True
            except subprocess.CalledProcessError as ex:
                if 'File exists.' in ex.output:
                    self.wait_takes_seconds = True
                else:
                    self.wait_takes_seconds = False
        return self.wait_takes_seconds

    def _check_restore_has_locks(self):
        '''Determine whether iptables-restore has locking built in.'''
        # The new version will have --wait just like iptables thanks to this patch:
        # http://patchwork.ozlabs.org/patch/739234/
        # Until then we'll need to do our own locking. So, this code detects whether we need to do locking
        if self.restore_has_locks is None:
            with open(os.devnull, 'w') as devnull:
                cmd = 'iptables-restore' if self.ver == 'ipv4' else 'ip6tables-restore'
                to_run = ["/usr/sbin/%s" % cmd, '--wait', '10', '--noflush']
                try:
                    subprocess.check_call(to_run, stderr=devnull, stdout=devnull)
                    self.restore_has_locks = True
                except subprocess.CalledProcessError:
                    self.restore_has_locks = False
        return self.restore_has_locks

    def exists(self):
        '''Return True if the chain exists or False otherwise'''
        try:
            # this is definitely going to throw. We're after the error message.
            subprocess.check_output(self._build_cmd('--rename-chain', self.chain, self.chain), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            if 'File exists.' in ex.output:
                return True
            if 'No chain/target/match by that name.' in ex.output:
                return False
        raise IpTablesChainError(msg="Failed to determine if chain exists",
                                 cmd=ex.cmd, exit_code=ex.returncode, output=ex.output)
    def get(self):
        '''Get all the rules of the chain'''
        cmd = self._build_cmd('--list-rules', self.chain)
        ipt = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = ipt.communicate()
        if ipt.returncode != 0:
            raise IpTablesChainError(msg="Failed to get existing chain rules",
                                     cmd=cmd, exit_code=ipt.returncode, output=err)
        return list([entry for entry in out.split('\n') if entry and not entry.startswith('-N ')])

    def set(self, rules):
        '''Set all the rules of the chain to match the passed in rules'''
        in_data = "*%s\n" % self.table
        # create the chain (if it didn't exist, otherwise this has no effect except to reset the counters)
        in_data += ":%s - [0:0]\n" % self.chain
        # flush the chain (if it did exist and had rules, otherwise this has no effect)
        in_data += "-F %s\n" % self.chain
        in_data += ("\n".join(rules))+"\n"
        in_data += "COMMIT\n"
        cmd = self._build_restore_cmd()
        # as seen on http://stackoverflow.com/questions/27803059/conditional-with-statement-in-python
        with open('/run/xtables.lock', 'a+') if not self._check_restore_has_locks() else DummyContextMgr() as fdnum:
            if not self._check_restore_has_locks():
                # do the locking ourselves
                start = time.time()
                locked = False
                while time.time() < start+600:
                    try:
                        # the lock will be released automatically when the with block goes out of scope
                        # and the file is closed.
                        fcntl.flock(fdnum, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        locked = True
                        break
                    except IOError as ex:
                        if ex.errno != errno.EDEADLK:
                            raise IpTablesChainError(msg="Failed to acquire iptables lock", exit_code=1)
                    time.sleep(0.5)
                if not locked:
                    raise IpTablesChainError(msg="Timed out trying to acquire iptables lock", exit_code=1)
            ipt = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = ipt.communicate(in_data)
            if ipt.returncode != 0:
                raise IpTablesChainError(msg="Failed to set chain rules",
                                         cmd=cmd, exit_code=ipt.returncode, output=out+"\n"+err)

def main():
    '''Ansible module to entirely manage a single iptables chain'''
    tables = ['filter', 'nat', 'mangle', 'raw', 'security']
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            rules=dict(required=True, type='list'),
            table=dict(required=False, default='filter', choices=tables),
            ip_version=dict(required=False, default='ipv4', choices=['ipv4', 'ipv6']),
        ),
        supports_check_mode=True
    )
    ver = module.params['ip_version']
    table = module.params['table']
    name = module.params['name']
    rules = module.params['rules']

    iptchain = IpTablesChain(table, name, ver)
    changed = False

    try:
        if (not iptchain.exists()) or iptchain.get() != rules:
            iptchain.set(rules)
            if not iptchain.exists():
                module.fail_json(msg="Chain create failed")
            elif iptchain.get() == rules:
                changed = True
            else:
                module.fail_json(msg="Chain update failed. Do input rules match 'iptables -S %s' output?" % name)

    except IpTablesChainError as ex:
        module.fail_json(msg=ex.msg)

    return module.exit_json(changed=changed, output="\n".join(rules))


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
