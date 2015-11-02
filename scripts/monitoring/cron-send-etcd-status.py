#!/usr/bin/env python
'''
   Command to send status of etcd to zabbix
'''

#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name

from openshift_tools.monitoring.zagg_sender import ZaggSender
import json
import requests

def main():
    ''' Get data from etcd API
    '''

    API_HOST = 'https://localhost:4001/v2/stats/store'
    SSL_CLIENT_CERT = '/etc/openshift/master/master.etcd-client.crt'
    SSL_CLIENT_KEY = '/etc/openshift/master/master.etcd-client.key'
    zs = ZaggSender()

    # Fetch the store statics from API
    try:
        request = requests.get(API_HOST, cert=(SSL_CLIENT_CERT, SSL_CLIENT_KEY), verify=False)
        content = json.loads(request.content)
        etcd_ping = 1

        # parse the items and add it as metrics
        zs.add_zabbix_keys({'openshift.master.etcd.create.success' : content['createSuccess']})
        zs.add_zabbix_keys({'openshift.master.etcd.create.fail' : content['createFail']})
        zs.add_zabbix_keys({'openshift.master.etcd.delete.success' : content['deleteSuccess']})
        zs.add_zabbix_keys({'openshift.master.etcd.delete.fail' : content['deleteFail']})
        zs.add_zabbix_keys({'openshift.master.etcd.get.success' : content['getsSuccess']})
        zs.add_zabbix_keys({'openshift.master.etcd.get.fail' : content['getsFail']})
        zs.add_zabbix_keys({'openshift.master.etcd.set.success' : content['setsSuccess']})
        zs.add_zabbix_keys({'openshift.master.etcd.set.fail' : content['setsFail']})
        zs.add_zabbix_keys({'openshift.master.etcd.update.success' : content['updateSuccess']})
        zs.add_zabbix_keys({'openshift.master.etcd.update.fail' : content['updateFail']})
        zs.add_zabbix_keys({'openshift.master.etcd.watchers' : content['watchers']})

    except requests.exceptions.ConnectionError as ex:
        print "ERROR talking to etcd API: %s" % ex.message
        etcd_ping = 0

    zs.add_zabbix_keys({'openshift.master.etcd.ping' : etcd_ping})

    # Finally, sent them to zabbix
    zs.send_metrics()

if __name__ == '__main__':
    main()
