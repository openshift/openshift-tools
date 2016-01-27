#!/usr/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name

"""
ops-runner: Script that runs commands and sends result data to zabbix.
"""

import argparse
import sys
from subprocess import Popen, PIPE, STDOUT
import random
import time
import re
import fcntl
import tempfile
import os
import atexit
import datetime
import socket

# Reason: disable pylint import-error because our libs aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender



NAME = "ops-runner"
OPS_RUNNER_LOG_FILE = "/var/log/%s.log" % NAME
OPS_RUNNER_LOCK_FILE_PREFIX = "/var/tmp/%s-" % NAME

OPS_RUNNER_DISC_KEY = 'disc.ops.runner'
OPS_RUNNER_DISC_MACRO = '#OSO_COMMAND'
OPS_RUNNER_EXITCODE_KEY = 'disc.ops.runner.command.exitcode'

class OpsRunner(object):
    """ class to run a command and report results to zabbix """

    def __init__(self):
        """ constructor """
        self.zagg_sender = ZaggSender()
        self.parse_args()
        self.tmp_file_handle = None
        self.lock_file_handle = None

    def create_tmp_file(self):
        """ Create the temporary file where command output is stored """
        prefix = NAME + '-' + self.args.name + "-"
        self.tmp_file_handle = tempfile.NamedTemporaryFile(prefix=prefix, mode='w', delete=False)

        # Ensure that we clean up the tmp file on exit
        atexit.register(self.cleanup)

    def cleanup(self):
        """ Cleans up resources when we're done (like the temp file). This runs on exit. """
        self.verbose_print("Removing temp file [%s]" % self.tmp_file_handle.name)
        self.tmp_file_handle.close()
        os.remove(self.tmp_file_handle.name)

    def verbose_print(self, msg):
        """ Prints a message if we're in verbose mode """
        if self.args.verbose:
            print msg

    @staticmethod
    def fail(msg):
        """ prints a message and then exits the script """
        print "ERROR: %s" % msg
        sys.exit(10)

    def run(self):
        """ main function to run the script """

        # Creating a file where all output will be written
        self.create_tmp_file()

        # We want to flock before we potentially sleep, just to keep multiple process
        # from running at the same time.
        if self.args.flock:
            lock_aquired = self.attempt_to_lock_file()
            if not lock_aquired:
                self.fail('this process is already running.')

        # Random Sleep if specified
        if self.args.random_sleep:
            seconds = random.randrange(int(self.args.random_sleep))
            self.verbose_print("Sleeping %s seconds..." % seconds)
            time.sleep(seconds)

        exit_code = self.run_cmd_with_output(self.args.rest)

        if self.args.flock:
            self.unlock_file()

        self.report_to_zabbix(OPS_RUNNER_DISC_KEY, OPS_RUNNER_DISC_MACRO,
                              OPS_RUNNER_EXITCODE_KEY, exit_code)

        self.verbose_print("CMD Exit code: %s" % exit_code)

        if exit_code != 0:
            # We need to close it so we can re-open it to read from
            self.tmp_file_handle.close()

            if os.access(OPS_RUNNER_LOG_FILE, os.W_OK):
                self.verbose_print("Non-zero exit code, writing output to %s" % OPS_RUNNER_LOG_FILE)
                self.log_output(exit_code)
            else:
                self.verbose_print("Non-zero exit code, writing output to logger.")
                self.run_cmd_with_output(['/usr/bin/logger', '-t', NAME, '-f',
                                          self.tmp_file_handle.name], log=False)

        sys.exit(exit_code)

    def log_output(self, exit_code):
        """ Copies the contents of the tmp file to the logfile """
        ts = time.time()
        date_str = datetime.datetime.fromtimestamp(ts).strftime("%b %d %H:%M:%S")
        hostname = socket.gethostname()

        with open(OPS_RUNNER_LOG_FILE, 'a') as log_output:
            log_output.write("%s %s %s: Exit code [%s]:~" % (date_str, hostname, NAME, exit_code))

            with open(self.tmp_file_handle.name, 'r') as tmp_input:
                for line in tmp_input:
                    # We don't want any newlines in the log file
                    line = re.sub('\n', "~", line)
                    log_output.write(line)

                log_output.write('\n')

    def report_to_zabbix(self, disc_key, disc_macro, key, value):
        """ Sends the commands exit code to zabbix. """
        zs = ZaggSender()

        self.verbose_print("Sending metric to zabbix - %s[%s]: %s" % (key, self.args.name, value))

        # Add the dynamic item
        #zs.add_zabbix_dynamic_item('disc.ops.runner', '#OSO_COMMAND', self.args.name)
        zs.add_zabbix_dynamic_item(disc_key, disc_macro, [key])

        # Send the value for the dynamic item
        zs.add_zabbix_keys({'%s[%s]' % (key, self.args.name): value})

        # Actually send them
        zs.send_metrics()

    def parse_args(self):
        """ parse the args from the cli """
        parser = argparse.ArgumentParser(description='ops-runner - Runs commands and reports results to zabbix.')
        parser.add_argument('-n', '--name', required=True, help='Name identifier for this command.')
        parser.add_argument('-f', '--flock', default=False, action="store_true",
                            help='Flock the command so that only one can run at ' + \
                                 'a time (good for cron jobs).')
        parser.add_argument('-s', '--random-sleep', help='Sleep time, random. Insert a random ' + \
                                                         'sleep between 1 and X number of seconds.')
        parser.add_argument('-v', '--verbose', default=False, action="store_true",
                            help='Makes ops-runner print more invormation.')
        parser.add_argument('rest', nargs=argparse.REMAINDER)

        self.args = parser.parse_args()

        # Ensure name is safe to use
        regex = r"[^A-Za-z0-9_.]"
        self.args.name = re.sub(regex, "_", self.args.name)

    def attempt_to_lock_file(self):
        """ Attempts to lock the lock file, returns False if it couldn't """
        try:
            lock_file = OPS_RUNNER_LOCK_FILE_PREFIX + self.args.name + ".lock"
            self.lock_file_handle = open(lock_file, 'w')
            fcntl.lockf(self.lock_file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            return False

    def unlock_file(self):
        """ Unlocks the lock file """
        fcntl.lockf(self.lock_file_handle, fcntl.LOCK_UN)

    def run_cmd_with_output(self, cmd, log=True):
        """ Runs a command and optionally logs it's output """
        process = Popen(cmd, stdout=PIPE, stderr=STDOUT,
                        universal_newlines=True)

        while True:
            out = process.stdout.read(1)
            if out == '' and process.poll() != None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()

                if log:
                    self.tmp_file_handle.write(out)
                    self.tmp_file_handle.flush()

        return process.returncode

if __name__ == "__main__":
    orunner = OpsRunner()
    orunner.run()
