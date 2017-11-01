#!/usr/bin/env python


''' Trello card CLI '''

import argparse
import json
import os
import sys
import json
import re

try:
    from urllib import urlencode
    from urllib2 import HTTPError, Request, urlopen
except ImportError:
    from urllib.error import HTTPError
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen

# constants
DEFAULT_LIST = "Active"
BASE_URL = "https://api.trello.com/1"

class Trello(object):
    """Trello object"""

    def __init__(self):
        """Set object params"""

        self.api_key = os.environ.get("trello_consumer_key", None)
        self.oauth_token = os.environ.get("trello_oauth_token", None)
        self.board_id = os.environ.get("trello_board_id", None)

        self.args = Trello.parse_args()

    @staticmethod
    def parse_args():
        """Parse CLI arguments"""
        parser = argparse.ArgumentParser(
            description='Create, comment, move Trello cards.')
        subparsers = parser.add_subparsers(help='sub-command help')

        parser_get = subparsers.add_parser('get',
                help='Get board information: card list, user list or card details')
        parser_get.add_argument(
            'card',
            nargs='?',
            metavar='CARD_URL',
            help='Card short URL to get details for')
        parser_get.add_argument(
            '--list', '-l',
            metavar='TRELLO_LIST',
            default=DEFAULT_LIST,
            help='List to display cards from, e.g. "Resolved" or "Snowflakes"')
        parser_get.add_argument(
            '--users', '-u',
            action='store_true',
            help='Display board users')
        parser_get.set_defaults(action='get')
        parser_create = subparsers.add_parser('create',
                                              help='Create a new card')
        parser_create.set_defaults(action='create')
        parser_create.add_argument(
            'title', metavar='TITLE',
            help='Card title')
        parser_create.add_argument(
            '--description', '-d', metavar='DESCRIPTION',
            help='Include a card description')
        parser_create.add_argument(
            '--assign', '-a', metavar='TRELLO_USERNAME',
            help='Comma-separated list of Trello IDs to assign to card')
        parser_update = subparsers.add_parser('update',
                                              help='Update an existing card')
        parser_update.set_defaults(action='update')
        parser_update.add_argument(
            'card', metavar='CARD', help='Existing card URL')
        parser_update.add_argument(
            '--comment', '-c',
            help='Add a comment')
        parser_update.add_argument(
            '--move', '-m',
            metavar='LIST_NAME',
            help='Move card to another list, e.g. "Resolved" or "Snowflakes"')
        parser_update.add_argument(
            '--assign', '-a',
            metavar='USER',
            help='Attach Trello user to card')
        parser_update.add_argument(
            '--unassign', '-u',
            metavar='USER',
            help='Remove Trello user from card')

        return parser.parse_args()

    def create(self):
        """Create card"""
        card = self.trello_create(self.args.title)
        print card['shortUrl']

    def update(self):
        """Update card"""
        if self.trello_update():
            print "Updated"
        else:
            sys.exit("No updates applied")

    def get(self):
        """Get card details or list of cards"""
        single = None
        cards = None
        if self.args.card:
            single = self.trello_get(self.card_id)
        else:
            cards = self.trello_get()
        if single:
            print json.dumps(single, indent=4)
        else:
            for card in cards:
                members = ''
                if self.args.users:
                    print card['username'], card['fullName']
                else:
                    for member in card['idMembers']:
                        if member:
                            members += str(self.member_username(member)) + ' '
                    print card['shortUrl'], card['name'], '(' + members + ')'

    def trello_update(self):
        """Call trello update API"""
        params = {}
        path = None
        update = False
        # Since the trello API is different calls/methods for different data
        # we call multiple times
        if self.args.comment:
            params['text'] = self.args.comment
            path = '/cards/' + self.card_id + '/actions/comments'
            self.make_request(path, "POST", params)
            update = True
        if self.args.move:
            params['idList'] = self.get_list_id(self.args.move)
            path = '/cards/' + self.card_id
            self.make_request(path, "PUT", params)
            update = True
        if self.args.assign:
            params['value'] = self.member_id(self.args.assign)
            path = '/cards/' + self.card_id + '/idMembers'
            self.make_request(path, "POST", params)
            update = True
        if self.args.unassign:
            #params['idMember'] = self.member_id(self.args.assign)
            path = '/cards/' + self.card_id + '/idMembers/' + self.member_id(self.args.unassign)
            self.make_request(path, "DELETE", params)
            update = True
        return update

    def trello_create(self, title):
        """Call trello create API"""
        params = {}
        params['idList'] = self.get_list_id()
        params['name'] = title
        if self.args.assign:
            params['idMembers'] = self.member_id(self.args.assign)
        if self.args.description:
            params['desc'] = self.args.description
        path = '/cards'
        return self.make_request(path, "POST", params)

    def member_username(self, memberid):
        """Get member username from member ID"""
        member = self.make_request('/members/' + memberid)
        return member['username']

    def member_id(self, username):
        """Get member id from username"""
        members = self.make_request('/boards/' + self.board_id + '/members/')
        for member in members:
            if username == member['username']:
                return member['id']

    @property
    def card_id(self):
        """Return parsed card ID from URL
           example: https://trello.com/c/PZlOHgGm
           returns: PZlOHgGm"""
        parsed_uri = self.args.card.split("/")
        return parsed_uri[-1]

    def get_list_id(self, list_id=None):
        """Return the list ID of default column"""
        default = DEFAULT_LIST
        if list_id:
            default = list_id
        path = '/boards/' + self.board_id + '/lists/'
        lists = self.make_request(path)
        # match board name regardless of case
        pattern = re.compile(default, re.I)
        for board_list in lists:
            if re.match(pattern, board_list['name']):
                return board_list['id']
        sys.exit("List '%s' not found" % list_id)

    def trello_get(self, card_id=None):
        """Get trello cards"""
        path = None
        if card_id:
            path = '/cards/' + card_id
        elif self.args.users:
            path = '/boards/' + self.board_id + '/members'
        else:
            path = '/lists/' + self.get_list_id(self.args.list) + '/cards'
        results = self.make_request(path)
        return results

    def make_request(self, path, method="GET", params=None):
        """Trello API call"""
        if not params:
            params = {}
        params['key'] = self.api_key
        params['token'] = self.oauth_token
        url = BASE_URL + path
        data = None
        if method == "GET":
            url += '?' + urlencode(params)
        elif method in ['DELETE', 'POST', 'PUT']:
            data = urlencode(params).encode('utf-8')
        request = Request(url)
        if method in ['DELETE', 'PUT']:
            request.get_method = lambda: method
        try:
            if data:
                response = urlopen(request, data=data)
            else:
                response = urlopen(request)
        except HTTPError as e:
            print(e)
            print(e.read())
            result = None
        else:
            result = json.loads(response.read().decode('utf-8'))

        return result


def main():
    """
    main() function
    :return:
    """
    trello = Trello()
    if trello.args.action is 'create':
        trello.create()
    elif trello.args.action is 'get':
        trello.get()
    elif trello.args.action is 'update':
        trello.update()

if __name__ == "__main__":
    main()
