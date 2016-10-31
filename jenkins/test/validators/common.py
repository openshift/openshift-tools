''' Provide common utils to validators '''
import subprocess
import sys

# Run cli command. By default, exit when an error occurs
def run_cli_cmd(cmd, exit_on_fail=True):
    '''Run a command and return its output'''
    proc = subprocess.Popen(cmd, bufsize=-1, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        if exit_on_fail:
            print stdout
            print "Unable to run " + " ".join(cmd) + " due to error: " + stderr
            sys.exit(proc.returncode)
        else:
            return False, stdout
    else:
        return True, stdout
