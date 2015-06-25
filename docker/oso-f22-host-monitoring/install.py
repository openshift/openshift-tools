#!/usr/bin/env python
'''
This script installs a pmda
'''

import pexpect
import os
import sys

def main():
    '''
    Pexpect script to install a pmda
    '''
    if len(sys.argv) == 1:
        sys.exit('Please specify a pmda.')

    for metric in sys.argv[1:]:
        os.chdir(os.path.join('/var/lib/pcp/pmdas', metric))
        child = pexpect.spawn('./Install')
        child.logfile = sys.stdout
        child.expect_exact('Please enter c(ollector) or m(onitor) or b(oth) [b] ')
        child.sendline('c' + os.linesep)
        child.expect(pexpect.EOF)

if __name__ == '__main__':
    main()
