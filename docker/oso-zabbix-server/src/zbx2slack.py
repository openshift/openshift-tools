#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''rst
zbx2slack-alert-notify.py
================================

Zabbix Alert Notification Script for Slack. by pure python.

`more read <https://github.com/laughk/zbx2slack/blob/master/README.rst>`_

LICENSE
------------------------
MIT

AUTHOR
------------------------
Kei Iwasaki <me@laughk.org>

FORKS
------------------------
https://github.com/laughk/zbx2slack
- original

https://github.com/drewandersonnz/zbx2slack
- modifications to support OpenShift Zabbix
'''

import os, sys
import re
import argparse
import json

try:
    '''for python3.x'''
    from urllib import request
except ImportError:
    '''for python2.x'''
    import urllib2 as request

__version__ = '0.1.1'
__scriptname__ = os.path.basename(__file__).replace('.py','')


class noticeInfo(object):
    def __init__(self, args):
        self.slack_botname     = args.slack_botname
        self.zabbix_server_url = args.zabbix_server_url

        self.trigger_id        = args.trigger_id
        self.trigger_name      = args.trigger_name
        self.trigger_status    = args.trigger_status
        self.trigger_severity  = args.trigger_severity
        self.trigger_url       = args.trigger_url
        self.event_id          = args.event_id
        self._item_text_list   = args.item
        self.items             = self._gen_items()

        self.trigger_url_gen   = self._gen_trigger_url()
        self.attachment_color  = self._gen_attachment_color()
        self.text              = self._gen_text()
        self.pretext           = self._gen_pretext()
        self.attachment_fields = self._gen_attachment_fields()

        self._payload = self._gen_payload()

    def _gen_trigger_url(self):
        '''
         generate and return url of Alert Trigger infomation.

         ex.
            http://zabbix.example.com/zabbix/tr_events.php?triggerid=00000&eventid=00
        '''
        _trigger_url = '{0}/tr_events.php?triggerid={1}&eventid={2}'.format(
                self.zabbix_server_url,
                self.trigger_id,
                self.event_id)
        return _trigger_url

    def _gen_items(self):

        """
        generate item dictionary

        from:

        [
          '{HOST.NAME1}|{ITEM.NAME1}|{ITEM.KEY1}|{ITEM.VALUE1}|{ITEM.ID1}',
          '{HOST.NAME2}|{ITEM.NAME2}|{ITEM.KEY2}|{ITEM.VALUE2}|{ITEM.ID2}',
        ]

        to:

        [
            { 'hostname': '{HOST.NAME1}',
              'name':     '{ITEM.NAME1}',
              'key':      '{ITEM.KEY1}',
              'value':    '{ITEM.VALUE1}',
              'id':       '{ITEM.ID1}'
            },

            { 'hostname': '{HOST.NAME2}',
              'name':     '{ITEM.NAME2}',
              'key':      '{ITEM.KEY2}',
              'value':    '{ITEM.VALUE2}',
              'id':       '{ITEM.ID2}'
            },
        ]

        """
        _items = [
            {
              'hostname': i[0],
              'name':     i[1],
              'key':      i[2],
              'value':    i[3],
              'id':       i[4]
            }
            for i in [
                item_text.split('|')
                for item_text in self._item_text_list
                    if not r'*UNKNOWN*' in item_text
            ]
        ]

        return _items


    def _gen_text(self):
        '''
        generate and return string for alert pretext, by the state.
        '''
        return "[{trigger_status}] [{trigger_severity}] {trigger_name}".format(**{
            "trigger_severity": self.trigger_severity,
            "trigger_status": self.trigger_status,
            "trigger_name": self.trigger_name,
        })

    def _gen_pretext(self):
        '''
        generate and return string for alert pretext, by the state.
        '''

        if self.trigger_status == 'PROBLEM':
            return ':boom: A problem occurred '
        elif self.trigger_status == 'OK':
            return ':white_check_mark: A problem recovered :+1:'
        else:
            return ':ghost::ghost: UNKNOWN :ghost::ghost:'

    def _gen_attachment_color(self):
        '''
        generate and return attchment color by the state.
        ref. https://api.slack.com/docs/attachments#color
        '''
        if self.trigger_status == 'PROBLEM':
            return 'danger'
        elif self.trigger_status == 'OK':
            return 'good'
        else:
            return 'warning'

    def _gen_attachment_fields(self):

        '''
        generate and return attchment fields for each items.
        ref. https://api.slack.com/docs/attachments#fields
        '''
        _fields = []

        for _item in self.items:

            _item_graph_url = '{0}/history.php?action=showgraph&itemids%5B%5D={id}'.format(
                    self.zabbix_server_url,
                    **_item)

            _fields.append({
                    'title': '{hostname} - {name}'.format(**_item),
                    'value': ':mag_right: {key} | *{value}* [<{0}|Graph>]'.format(_item_graph_url, **_item)
                    })

        return _fields


    def _gen_payload(self):
        '''
        generate and return payload for posting to slack.
        ref. https://api.slack.com/docs/attachments#fields
        '''

        _payload = json.dumps({
            'username': self.slack_botname,
            'text': self.text,
            'attachments': [
                {
                    'title': self.trigger_url,
                    'title_link': self.trigger_url,
                },
                {
                    'color': self.attachment_color,
                    'fields': self.attachment_fields,
                    'title': self.trigger_name,
                    'title_link': self.trigger_url_gen,
                    #'pretext': self.pretext,
                    'mrkdwn_in': [
                        'title', 'pretext', 'fields'
                    ],
                },
            ]
        })

        if isinstance(_payload, str):
            return _payload.encode('utf-8')

        return _payload

    @property
    def payload(self):
        return self._payload


def alert_to_slack(payload, slack_incoming_webhook):

    request_header = {'Content-Type': 'application/json'}
    req = request.Request(
            slack_incoming_webhook,
            payload,
            request_header)
    request.urlopen(req)


def main():


    '''
    Environment Check and merge to SCRIPT_ENV
    -------------------------------

    {{{
    '''
    SCRIPT_ENV = {
        'ZABBIX_SERVER_URL': '',
        'INCOMING_WEBHOOK_URL': ''
    }

    for env in SCRIPT_ENV.keys():
        if env in os.environ.keys():
            SCRIPT_ENV[env] = os.environ[env]
    '''
    ------------------------------
    }}}
    '''


    '''
    Analyze options
    -------------------------------

    ex.

        $ zbx2slack-alert-notify.py \
            --zabbix-server-url "http://zabbix.example.com/zabbix" \
            --slack-botname "Zabbix Alert" \
            --slack-incoming-webhook-url "https://hooks.slack.com/services/xxxxxxxxx/xxxxxxxxx/...." \
            --trigger-id "{TRIGGER.ID}" \
            --trigger-name "{TRIGGER.NAME}" \
            --trigger-status "{TRIGGER.STATUS}" \
            --trigger-severity "{TRIGGER.SEVERITY}" \
            --trigger-url "{TRIGGER.URL}" \
            --event-id "{EVENT.ID}" \
            --item "{HOST.NAME1}|{ITEM.NAME1}|{ITEM.KEY1}|{ITEM.VALUE1}|{ITEM.ID1}" \
            --item "{HOST.NAME2}|{ITEM.NAME2}|{ITEM.KEY2}|{ITEM.VALUE2}|{ITEM.ID2}" \
            --item "{HOST.NAME3}|{ITEM.NAME3}|{ITEM.KEY3}|{ITEM.VALUE3}|{ITEM.ID3}"

    {{{

    '''

    parser = argparse.ArgumentParser(
            description='Zabbix Alert Notification Script for Slack.')

    parser.add_argument('--zabbix-server-url',
            default=SCRIPT_ENV['ZABBIX_SERVER_URL'],
            help='Your Zabbix server URL (Default: "")'.format(SCRIPT_ENV['ZABBIX_SERVER_URL']),
            type=str)

    parser.add_argument('--slack-botname', default='Zabbix Alert',
            type=str, help='Slack Bot name (Default: "Zabbix Alert")')
    parser.add_argument('--slack-incoming-webhook-url',
            default=SCRIPT_ENV['INCOMING_WEBHOOK_URL'],
            help='Slack Bot name (Default: "{0}")'.format(SCRIPT_ENV['INCOMING_WEBHOOK_URL']),
            type=str)

    parser.add_argument('--trigger-id',
            type=int, help='Set Zabbix Macro "{TRIGGER.ID}"')
    parser.add_argument('--trigger-name',
            type=str, help='Set Zabbix Macro "{TRIGGER.NAME}"')
    parser.add_argument('--trigger-status',
            type=str, help='Set Zabbix Macro "{TRIGGER.STATUS}"' )
    parser.add_argument('--trigger-severity',
            type=str, help='Set Zabbix Macro "{TRIGGER.SEVERITY}"')
    parser.add_argument('--trigger-url',
            type=str, help='Set Zabbix Macro "{TRIGGER.URL}"')
    parser.add_argument('--event-id',
            type=int, help='Set Zabbix Macro "{EVENT.ID}"')
    parser.add_argument('--item', action='append',
            type=str, help='Set Zabbix Macro formated by'
                           '"{HOST.NAME1}|{ITEM.NAME1}|{ITEM.KEY1}|{ITEM.VALUE1}|{ITEM.ID1}"')

    parser.add_argument('--version', action='version',
            version='{0} {1}'.format(__scriptname__, __version__))

    args = parser.parse_args()

    '''
    --------------------------------
    }}}
    '''

    notice = noticeInfo(args)
    alert_to_slack(
            notice.payload,
            args.slack_incoming_webhook_url)


if __name__ == '__main__':
    main()
