""" Miscellaneous helper functions to be used throughout CI """

import subprocess
import sys

def run_cli_cmd(cmd, exit_on_fail=True, log_cmd=True):
    '''Run a command and return its output'''
    # Don't log the command if log_cmd=False to avoid exposing secrets in commands
    if log_cmd:
        print "> " + " ".join(cmd)
    proc = subprocess.Popen(cmd, bufsize=-1, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                            shell=False)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        # Don't log the command if log_cmd=False to avoid exposing secrets in commands
        if log_cmd:
            print "Unable to run " + " ".join(cmd) + " due to error: " + stderr
        else:
            print "Error running system command: " + stderr
        if exit_on_fail:
            sys.exit(proc.returncode)
        else:
            return False, stdout
    else:
        return True, stdout
