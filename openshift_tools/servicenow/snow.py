#!/usr/bin/env python


''' Service Now ticket CLI '''

import argparse
import os
import json
from ticketutil.servicenow import ServiceNowTicket # pylint: disable=import-error

class ServiceNow(object):
    """SNOW object"""

    def __init__(self):
        """Set object params"""

        self.url = os.environ.get("snowurl", None)
        self.username = os.environ.get("snowuser", None)
        self.password = os.environ.get("snowpass", None)

        self.args = ServiceNow.parse_args()

        self.ticket = ServiceNowTicket(url=self.url,
                                       project='incident',
                                       auth=(self.username, self.password))

    @staticmethod
    def parse_args():
        """Parse CLI arguments"""
        parser = argparse.ArgumentParser(
            description='Create, update, query and close Service Now tickets.')
        subparsers = parser.add_subparsers(help='sub-command help')
        common_args = argparse.ArgumentParser(add_help=False)
        common_args.add_argument(
            '--assigned-to', '-a', metavar='USER', help='SNOW user to assign ticket to')
        common_args.add_argument(
            'extra', metavar='KEY=VAL', nargs='*',
            help='Other SNOW key=value pairs (SNOW implementation-dependent)')

        parser_create = subparsers.add_parser('create', parents=[common_args],
                                              help='Create a new ticket')
        parser_create.add_argument(
            '--short-description', '-d', metavar='SHORT DESCRIPTION',
            help='Short ticket description')
        parser_create.add_argument('--description', '-D', metavar='LONG DESCRIPTION',
                                   help='Long ticket description')
        parser_create.add_argument('--category', '-C', metavar='CATEGORY', default='incident',
                                   help='Ticket category')
        parser_create.add_argument('--priority', '-p', metavar='PRIORITY',
                                   help='Ticket priority')
        parser_create.set_defaults(action='create')

        parser_update = subparsers.add_parser('update', parents=[common_args],
                                              help='Update an existing ticket')
        parser_update.set_defaults(action='update')
        parser_update.add_argument(
            'ticketid', metavar='TICKETID', help='Existing ticket ID')
        parser_update.add_argument(
            '--status', '-s',
            choices=['New', 'In Progress', 'On Hold', 'Resolved', 'Closed', 'Canceled'],
            help='Ticket status')
        parser_update.add_argument('--comment', '-c', help='Ticket comment')

        parser_close = subparsers.add_parser('close', help='Close an existing ticket')
        parser_close.set_defaults(action='close')
        parser_close.add_argument('ticketid', metavar='TICKETID', help='Existing ticket ID')

        parser_get = subparsers.add_parser('get', help='Get ticket details')
        parser_get.set_defaults(action='get')
        parser_get.add_argument('ticketid', metavar='TICKETID', help='Existing ticket ID')

        return parser.parse_args()

    @property
    def extra_args(self):
        """Return extra SNOW CLI args as k:v dict"""
        extra_args = dict()
        for arg in self.args.extra:
            key, val = arg.split('=')
            extra_args[key] = val
        return extra_args

    def create(self, **kwargs):
        """Create service now ticket"""
        self.ticket.create(short_description=self.args.short_description,
                           description=self.args.description,
                           category=self.args.category,
                           item='',
                           **kwargs)
        _ticket = self.ticket.get_ticket_content()
        print _ticket.ticket_content['number']

    def update(self, ticket_id, **kwargs):
        """Update service now ticket"""
        self.ticket.set_ticket_id(ticket_id)
        if self.args.comment:
            self.ticket.add_comment(self.args.comment)
        if self.args.status:
            self.ticket.change_status(self.args.status)
        if self.args.assigned_to:
            self.ticket.edit(assigned_to="self.args.assigned_to")
        if kwargs:
            self.ticket.edit(**kwargs)
        print "Updated %s" % ticket_id

    def close(self, ticket_id):
        """Close service now ticket"""
        _ticket = self.ticket.set_ticket_id(ticket_id)
        self.ticket.change_status('Closed')
        print "Closed %s" % _ticket.ticket_content['number']

    def get(self, ticket_id):
        """Print service now ticket contents"""
        _ticket = self.ticket.get_ticket_content(ticket_id)
        print json.dumps(_ticket.ticket_content, indent=4, sort_keys=True)

def main():
    """
    main() function
    :return:
    """
    snow = ServiceNow()
    if snow.args.action is 'create':
        snow.create(**snow.extra_args)
    elif snow.args.action is 'update':
        snow.update(snow.args.ticketid, **snow.extra_args)
    elif snow.args.action is 'close':
        snow.close(snow.args.ticketid)
    elif snow.args.action is 'get':
        snow.get(snow.args.ticketid)
    snow.ticket.close_requests_session()

if __name__ == "__main__":
    main()
