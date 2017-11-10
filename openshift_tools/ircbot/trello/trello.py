#!/usr/bin/env python

''' Interact with Trello API as a CLI or Sopel IRC bot module '''

import argparse
import json
import os
import re
import sys

# sopel is only for IRC bot installation. Not required for CLI
try:
    import sopel.module # pylint: disable=import-error
except ImportError:
    pass

try:
    from urllib import urlencode
    from urllib2 import HTTPError, Request, urlopen
except ImportError:
    from urllib.error import HTTPError
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen

# constants
DEFAULT_LIST = "Active"
DEFAULT_RESOLVED_LIST = "Resolved"
BASE_URL = "https://api.trello.com/1"

class Trello(object):
    """Trello object"""

    def __init__(self):
        """Set object params"""

        self.args = None
        self.api_key = os.environ.get("trello_consumer_key", None)
        self.oauth_token = os.environ.get("trello_oauth_token", None)
        self.board_id = os.environ.get("trello_board_id", None)

    @staticmethod
    def parse_args():
        """Parse CLI arguments"""
        parser = argparse.ArgumentParser(
            description='Create, comment, move Trello cards.')
        subparsers = parser.add_subparsers(help='sub-command help')

        parser_get = subparsers.add_parser('get',
                                           help="""Get board information:
                                                   card list, user list or
                                                   card details""")
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

    def create(self, title=None):
        """Create card"""
        if not title:
            title = self.args.title
        card = self.trello_create(title)
        return card['shortUrl']

    def update(self):
        """Update card"""
        if self.trello_update(self.card_id(self.args.card)):
            print("Updated")
        else:
            sys.exit("No updates applied")

    def get(self):
        """Get card details or list of cards"""
        cards = None
        if self.args.card:
            return json.dumps(self.trello_get(self.card_id()), indent=4)
        cards = self.trello_get()
        results = ''
        for card in cards:
            members = ''
            if self.args.users:
                results += '{} {}\n'.format(str(card['username']),
                                            str(card['fullName']))
            else:
                for member in card['idMembers']:
                    if member:
                        members += str(self.member_username(member)) + ' '
                results += '{} {} ({})\n'.format(str(card['shortUrl']),
                                                 str(card['name']),
                                                 members)
        return results

    def trello_update(self, card_id, **kwargs):
        """Call trello update API
        :param card_id: card ID
        :return: success boolean"""
        params = {}
        path = None
        updated = False
        # handle being called via CLI or bot
        if self.args:
            if self.args.comment:
                kwargs['comment'] = self.args.comment
            if self.args.move:
                kwargs['move'] = self.args.move
            if self.args.assign:
                kwargs['assign'] = self.args.assign
            if self.args.unassign:
                kwargs['unassign'] = self.args.unassign
        # Since the trello API is different calls/methods for different data
        # we call multiple times
        if 'comment' in kwargs:
            params['text'] = kwargs['comment']
            path = '/cards/' + card_id + '/actions/comments'
            updated = self.make_request(path, "POST", params)
        if 'resolve' in kwargs:
            params['idList'] = self.get_list_id(DEFAULT_RESOLVED_LIST)
            path = '/cards/' + card_id
            updated = self.make_request(path, "PUT", params)
        if 'move' in kwargs:
            params['idList'] = self.get_list_id(kwargs['move'])
            path = '/cards/' + card_id
            updated = self.make_request(path, "PUT", params)
        if 'assign' in kwargs:
            params['value'] = self.member_id(kwargs['assign'])
            path = '/cards/' + card_id + '/idMembers'
            updated = self.make_request(path, "POST", params)
        if 'unassign' in kwargs:
            path = '/cards/' + card_id + '/idMembers/' + self.member_id(kwargs['unassign'])
            updated = self.make_request(path, "DELETE", params)
        return updated

    def trello_create(self, title):
        """Call trello create API
        :param title: name/title of card
        :return: card"""
        params = {}
        params['idList'] = self.get_list_id()
        params['name'] = title
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

    def card_id(self, url=None):
        """Return parsed card ID from URL
           example: https://trello.com/c/PZlOHgGm
           returns: PZlOHgGm
        :param url: trello short URL
        :return: trello card ID"""
        if not url:
            url = self.args.card
        parsed_uri = url.split("/")
        return parsed_uri[-1]

    def get_list_id(self, list_id=None):
        """Return the list ID
        :param list_id: list ID if not default
        :return: list_id"""
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
        """Get trello cards
        :param card_id: trello card ID
        :return: trello json"""
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
        """Trello API call
        :param path: trello API path
        :param method: rest call method
        :param params: API params
        :return: trello json"""
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
        except HTTPError as err:
            print(err)
            print(err.read())
            result = None
        else:
            result = json.loads(response.read().decode('utf-8'))

        return result

def get_trello_id(ircnick):
    """Return trello ID for a given IRC nick"""
    key = 'IRCNICK_' + ircnick
    try:
        return os.environ[key]
    except KeyError:
        print("%s, you need to map your IRC nick with Trello username" % ircnick)
        return None

@sopel.module.commands('issue')
def issue(bot, trigger):
    """Record a new issue in Trello, e.g. '.issue Some issue text'"""
    trellobot = Trello()
    card = trellobot.trello_create(trigger.group(2))
    bot.say(card['shortUrl'])
    if not trellobot.trello_update(trellobot.card_id(card['shortUrl']),
                                   assign=get_trello_id(trigger.nick)):
        bot.reply(
            "you need to map your IRC nick with Trello username." +
            "See https://github.com/openshift/openshift-ansible-ops/tree/prod/playbooks/adhoc/ircbot")

@sopel.module.commands('comment')
def comment(bot, trigger):
    """Add comment to a trello card, e.g. '.comment <trelloShortUrl> My comment'"""
    trellobot = Trello()
    msg = trigger.group(2).partition(' ')
    trellobot.trello_update(trellobot.card_id(msg[0]), comment=msg[2])
    bot.say('Comment added')

@sopel.module.commands('resolve', 'resolved')
def resolve(bot, trigger):
    """Resolve a trello card, e.g. '.resolve <trelloShortUrl>'"""
    trellobot = Trello()
    if trellobot.trello_update(trellobot.card_id(trigger.group(2)), resolve=True):
        card = trellobot.trello_get(trellobot.card_id(trigger.group(2)))
        bot.say('Resolved {}: {}'.format(trigger.group(2), card['name']))
    else:
        bot.say('Could not resolve %s' % trigger.group(2))

def main():
    """
    main() function
    :return:
    """
    trello = Trello()
    trello.args = Trello.parse_args()
    if trello.args.action is 'create':
        print(trello.create())
    elif trello.args.action is 'get':
        print(trello.get())
    elif trello.args.action is 'update':
        trello.update()

if __name__ == "__main__":
    main()
