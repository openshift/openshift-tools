#!/usr/bin/env python
'''
   Command to send status of etcd to zabbix
'''

#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name

from openshift_tools.monitoring.zagg_sender import ZaggSender
import json
import yaml
import requests

def main():
    ''' Get data from etcd API
    '''

    SSL_CLIENT_CERT = '/etc/openshift/master/master.etcd-client.crt'
    SSL_CLIENT_KEY = '/etc/openshift/master/master.etcd-client.key'
    OPENSHIFT_MASTER_CONFIG = '/etc/openshift/master/master-config.yaml'

    # find out the etcd port
    with open(OPENSHIFT_MASTER_CONFIG, 'r') as f:
        config = yaml.load(f)

    API_HOST = config["etcdClientInfo"]["urls"][0]

    # define the store API URL
    API_URL = API_HOST + "/v2/stats/store"


    zs = ZaggSender()
    # Fetch the store statics from API
    try:
        request = requests.get(API_URL, cert=(SSL_CLIENT_CERT, SSL_CLIENT_KEY), verify=False)
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
