#!/usr/bin/env python
'''
Email script for zabbix notifications
'''

import smtplib
import sys
import yaml

def get_config():
    '''Fetch the zabbix config credentials
    '''
    return yaml.load(open('/etc/openshift_tools/zabbix_actions.yml'))

def email():
    '''send email for zabbix
    '''

    config = get_config()

    mailfrom = config.get('ses_mail_from', None)
    smtpdomain = config.get('ses_smtp_domain', None)
    smtpserver = config.get('ses_smtp_server', None)
    username = config.get('ses_user', None)
    password = config.get('ses_password', None)
    if any([var == None for var in  [mailfrom, smtpserver, smtpdomain, username, password]]):
        print 'Please provide the necessary variables.'
        sys.exit(1)

    to_addr = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]

    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (mailfrom, ", ".join(to_addr.split(',')), subject))

    msg += body

    server = smtplib.SMTP_SSL(smtpserver, 465, smtpdomain)
    # server.set_debuglevel(1)
    server.login(username, password)
    server.sendmail(mailfrom, to_addr, msg)
    server.quit()


if __name__ == '__main__':
    email()

