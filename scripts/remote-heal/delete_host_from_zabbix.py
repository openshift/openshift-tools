#!/usr/bin/env python
# coding=utf-8
# pylint: disable=invalid-name
# pylint: disable=import-error
# pylint: disable=broad-except
"""
delete zag pod
"""
import sys
from pyzabbix import ZabbixAPI

if len(sys.argv) == 2:
    hostname = sys.argv[1]
else:
    sys.exit("please use $0 <hostname>")

#check if this is a pod or a host
target_str = 'oso-rhel7-zagg-web'
if hostname.find(target_str) == -1:
    sys.exit("not a auto heal pod ")
else:
    pass


usernameline = ""
passwordline = ""
with open("/etc/openshift_tools/zabbix-config.env") as f:
    for line in f:
        try:
            if line.index("ZABBIX_USER"):
                usernameline = line
            elif line.index("PASSWORD"):
                passwordline = line
        except Exception, e:
            print e
            if line.index("PASSWORD"):
                passwordline = line

usernameline_d = usernameline.split("=")
username = usernameline_d[1]

passwordline_d = passwordline.split("=")
passwd = passwordline_d[1].replace("'", "")



zapi = ZabbixAPI("https://zabbix.ops-aws.openshift.com/zabbix")
zapi.session.verify = False
zapi.login(username, passwd)
#print("Connected to Zabbix API Version %s" % zapi.api_version())
#get host info
hostinfo = zapi.host.get(output="extend", filter={"host":hostname})
if hostinfo:
    print hostinfo
    #start delete the host from Zabbix
    hostid = int(hostinfo[0]['hostid'])
    print hostid
    hostdeleteinfo = zapi.host.delete(hostid)
    print hostdeleteinfo
else:
    print 'nohostfound'
