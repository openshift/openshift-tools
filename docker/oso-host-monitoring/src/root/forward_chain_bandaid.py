#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4

#FIXME: This script is not packaged. That goes against team policy.
#FIXME: This script must be removed or packaged.
# Script added in violation of policy because:
#  1. we're in a hurry to get it rolled out because of a related, current outage
#  2. this script should go away within a few weeks when it gets obsoleted by
#     https://github.com/openshift/origin/pull/13465

'''
This entire script is a band-aid that needs to be in place until
https://github.com/openshift/origin/pull/13465 is merged and
backported to 3.4 and 3.5 and the hotfix that contains it is installed
on all clusters.

This script will:
1. create the OPENSHIFT-OUTPUT-FILTERING chain in the filter table
   (if it doesn't exist)
2. check to see if https://github.com/openshift/origin/pull/13465 is
   doing its thing
3. if not, it will make sure that an equivalent rule to jump to
   OPENSHIFT-OUTPUT-FILTERING is present in the FORWARD chain and
   that it is the top rule.

For best effect, run it frequently from cron so that any reordering
can be quickly remedied.
'''

import os
import subprocess
import fcntl
import errno
import time

# the rule that must be the first thing in the FORWARD chain.
# The "! -s 0.0.0.1/32" is present only so that we can tell OUR_RULE from THEIR_RULE
OUR_RULE = '-A FORWARD ! -s 0.0.0.1/32 -i tun0 ! -o tun0 -j OPENSHIFT-OUTPUT-FILTERING'
# the rule that we're waiting for that will be added by the product. If we see this, our rule is no longer needed
THEIR_RULE = '-A FORWARD -i tun0 ! -o tun0 -j OPENSHIFT-OUTPUT-FILTERING'
# chain we're jumping to
JUMP_CHAIN_NAME = 'OPENSHIFT-OUTPUT-FILTERING'
# chain we're jumping from
SOURCE_CHAIN_NAME = 'FORWARD'

class TopRuleError(Exception):
    '''All IpTablesChain methods throw this exception when errors occur'''
    def __init__(self, msg, cmd, exit_code, output):
        super(TopRuleError, self).__init__(msg)
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

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
class TopRule(object):
    '''A single rule that should be at the top of the chain'''

    def __init__(self, table, source_chain, jump_chain, ver, top_rule, noop_rule):
        '''Create the TopRule object to ensure that the rule is at the top of the chain'''
        self.table = table
        self.source_chain = source_chain
        self.jump_chain = jump_chain
        self.ver = ver
        self.top_rule = top_rule
        self.noop_rule = noop_rule
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
                self.wait_takes_seconds = bool('File exists.' in ex.output)
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

    def jump_chain_exists(self):
        '''Return True if the jump chain exists or False otherwise'''
        try:
            # this is definitely going to throw. We're after the error message.
            subprocess.check_output(self._build_cmd('--rename-chain', self.jump_chain, self.jump_chain),
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            if 'File exists.' in ex.output:
                return True
            if 'No chain/target/match by that name.' in ex.output:
                return False
        raise TopRuleError(msg="Failed to determine if chain exists",
                           cmd=ex.cmd, exit_code=ex.returncode, output=ex.output)
    def get(self):
        '''Get all the rules of the chain'''
        cmd = self._build_cmd('--list-rules', self.source_chain)
        ipt = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = ipt.communicate()
        if ipt.returncode != 0:
            raise TopRuleError(msg="Failed to get existing chain rules",
                               cmd=cmd, exit_code=ipt.returncode, output=err)
        return list([entry for entry in out.split('\n') if entry and not entry.startswith('-N ')])

    def set(self):
        '''Set all the rules of the chain to match the passed in rules'''
        existing_rules = self.get()
        updated_rules = [rule for rule in existing_rules if rule != self.top_rule]
        if self.noop_rule not in updated_rules:
            # find position to insert it. either just before the first -A rule, or at the end if there aren't any
            enumeration = (i for i, rule in enumerate(updated_rules) if rule.startswith('-A'))
            pos = next(enumeration, len(updated_rules))
            updated_rules.insert(pos, self.top_rule)
        if existing_rules == updated_rules:
            # nothing to do, everything already looks good. early return
            return
        in_data = "*%s\n" % self.table
        if not self.jump_chain_exists():
            # create the jump_chain
            in_data += ":%s - [0:0]\n" % self.jump_chain
        # assume that source_chain already exists
        # flush the source_chain since we're about to recreate its rules
        in_data += "-F %s\n" % self.source_chain
        in_data += ("\n".join(updated_rules))+"\n"
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
                            raise TopRuleError(msg="Failed to acquire iptables lock", exit_code=1, cmd='', output='')
                    time.sleep(0.5)
                if not locked:
                    raise TopRuleError(msg="Timed out trying to acquire iptables lock", exit_code=1, cmd='', output='')
            ipt = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = ipt.communicate(in_data)
            if ipt.returncode != 0:
                raise TopRuleError(msg="Failed to set chain rules",
                                   cmd=cmd, exit_code=ipt.returncode, output=out+"\n"+err)

def main():
    '''Band-aid script to ensure that the OpenShift filter rule is always at the top of the FORWARD chain'''

    toprule = TopRule('filter', SOURCE_CHAIN_NAME, JUMP_CHAIN_NAME, 'ipv4', OUR_RULE, THEIR_RULE)

    toprule.set()

if __name__ == '__main__':
    main()
