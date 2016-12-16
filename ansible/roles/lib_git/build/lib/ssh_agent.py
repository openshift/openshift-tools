"""Run an ssh agent and set SSH_AUTH_SOCK so that clients will use it

Example:
    with ssh_agent.SshAgent() as agent:
        agent.add_key(private_key_string)
        # do ssh stuff
    # as agent loses scope, the ssh agent is killed
"""

from __future__ import with_statement
import atexit
import tempfile
import os
import sys
import shutil
import subprocess
import random
import time
import datetime

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
