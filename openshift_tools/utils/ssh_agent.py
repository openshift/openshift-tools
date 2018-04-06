#!/usr/bin/env python
"""Run an ssh agent and set SSH_AUTH_SOCK so that clients will use it

Example:
    with ssh_agent.SshAgent() as agent:
        agent.add_key(private_key_string)
        # do ssh stuff
    # as agent loses scope, the ssh agent is killed
"""

from __future__ import with_statement
import atexit
import base64
import datetime
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time

from hashlib import md5
from Crypto.Cipher import AES

class SshAgentException(Exception):
    """An exception thrown for problems in SshAgent
    """
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(SshAgentException, self).__init__(message)

class SshAgent(object):
    """Run an ssh agent and set SSH_AUTH_SOCK so that clients will use it.

    The running agent can have one or more keys added (via the SshAgent.add_key()
    method or via any other method that can find and talk to the running agent.
    """

    class Cleanup(object):
        """A helper functor class for SshAgent

        An object of this class can be passed
        directly to atexit, which will call __call__() when the
        program exits
        """
        def __init__(self, ssh_agent, ssh_auth_sock_dir):
            self.ssh_agent = ssh_agent
            self.ssh_auth_sock_dir = ssh_auth_sock_dir
            self.cleaned_up = False
            self.original_env_var = os.environ.get('SSH_AUTH_SOCK')

        def __call__(self):
            if self.cleaned_up:
                return
            self.cleaned_up = True
            try:
                shutil.rmtree(self.ssh_auth_sock_dir, ignore_errors=True)
            except OSError:
                pass
            try:
                self.ssh_agent.kill()
            except OSError:
                pass
            if self.original_env_var:
                os.environ['SSH_AUTH_SOCK'] = self.original_env_var
            else:
                del os.environ['SSH_AUTH_SOCK']

        def pass_(self):
            """A function to appease pylint"""
            pass

        def pass__(self):
            """Another function to appease pylint"""
            self.pass_()

    def __init__(self):
        devnull = open(os.devnull, 'w')
        # Start an ssh-agent process and register it to be killed atexit
        self.ssh_auth_sock_dir = tempfile.mkdtemp(prefix=os.path.basename(sys.argv[0]) + '.')
        self.ssh_auth_sock = os.path.join(self.ssh_auth_sock_dir, "ssh_agent")
        self.ssh_agent = subprocess.Popen(["ssh-agent", "-d", "-a", self.ssh_auth_sock], stdout=devnull, stderr=devnull)
        self.cleanup = self.Cleanup(self.ssh_agent, self.ssh_auth_sock_dir)
        # this is here so that when python exits, we make sure that the agent is killed
        # (in case python exits before our __del__() is called
        atexit.register(self.cleanup)
        os.environ["SSH_AUTH_SOCK"] = self.ssh_auth_sock

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tback):
        self.cleanup()

    def __del__(self):
        self.cleanup()

    def kill(self):
        '''Explicitly kill the running ssh-agent

        It's not necessary to call this function as the agent
        will be cleaned up automatically.
        '''
        self.cleanup()

    def add_key(self, key):
        """Add a key to the running agent.

        Note:
            This function can be called any number of times to add multiple keys.

        Args:
            key (str): A string containing the ssh private key to be added (the
                    actual key data, not the filename of a key)
        Raises:
            SshAgentException: when ssh-add does not immediately return (as in the
                    case of a private key with a passphrase)
        """

        #if self.ssh_agent.poll() is None:
        #    raise SshAgentException("Unable to add ssh key. Did agent die?")

        named_pipe_path = os.path.join(self.ssh_auth_sock_dir, "keypipe." + str(random.getrandbits(64)))
        try:
            os.mkfifo(named_pipe_path, 0600)
        except OSError, exception:
            print "Failed to create FIFO: %s" % exception

        devnull = open(os.devnull, 'w')
        ssh_add = subprocess.Popen(["ssh-add", named_pipe_path], stdout=devnull, stderr=devnull)
        fifo = open(named_pipe_path, 'w')
        print >> fifo, key
        fifo.close()

        #Popen.wait() doesn't have a timeout, so we'll implement one using poll() :(
        start_time = datetime.datetime.now()
        while ssh_add.poll() is None:
            if (datetime.datetime.now() - start_time).total_seconds() > 5:
                try:
                    ssh_add.kill()
                except OSError:
                    pass
                raise SshAgentException("Unable to add ssh key. Timed out. Does key have a passphrase?")
            time.sleep(0.1)
        os.remove(named_pipe_path)

    # from https://stackoverflow.com/questions/16761458/how-to-decrypt-openssl-aes-encrypted-files-in-python
    @staticmethod
    def derive_key_and_iv(password, salt, key_length, iv_length):
        """ derive the key and iv for decrypting ssh keys """

        derived = d_i = b''
        while len(derived) < key_length + iv_length:
            d_i = md5(d_i + password + salt).digest()
            derived += d_i
        return derived[:key_length], derived[key_length:key_length+iv_length]

    # adapted from https://stackoverflow.com/questions/16761458/how-to-decrypt-openssl-aes-encrypted-files-in-python
    @staticmethod
    def decrypt(ciphertext, password, key_length=32):
        """ decrypt the key """

        salt = ciphertext[len('Salted__'):AES.block_size]
        key, init_v = SshAgent.derive_key_and_iv(password, salt, key_length, AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, init_v)
        retval = cipher.decrypt(ciphertext[AES.block_size:])
        padding_length = ord(retval[-1])
        return retval[:-padding_length]

    # decrypt the private key using the passphrase, then add it to the agent
    def add_autokey(self, key_path, key_prefix):
        """ add autokeys """

        key_prefix_path = os.path.join(key_path, key_prefix)

        for week in ['even', 'odd']:
            passfn = '{}.{}.passphrase.txt'.format(key_prefix_path, week)
            passphrase = None
            with open(passfn, 'r') as passf:
                for line in passf:
                    if len(line) > 0 and line[0] != '#':
                        passphrase = line.strip()
                        break
            if not passphrase:
                raise SshAgentException("Unable to find passphrase in file {}".format(passfn))
            with open('{}.{}.private.aes256.txt'.format(key_prefix_path, week), 'r') as pkf:
                keydata = SshAgent.decrypt(base64.b64decode(pkf.read()), passphrase)
                self.add_key(keydata)
