# coding=utf-8
# pylint: disable=protected-access
# pylint: disable=import-error
"""
openshift_sre.py - Various helper modules for OpenShift Online SRE team
Copyright © 2017, Will Gordon <wgordon@redhat.com>
Licensed under the MIT license.
"""
from __future__ import print_function
from __future__ import unicode_literals
import datetime
from re import finditer
import json
import os
import pypd
from sopel import module
from sopel import formatting

###########################
# Configuration constants #
###########################
DEBUG = False  # Debug sends debug messages to the bot owner via PRIVMSG
SNOW_TICKET_REGEX = r'\b(?<!=)(?P<ticket>(TASK|REQ|RITM|INC|PRB|CHG)[0-9]{7})\b'
SFDC_CASE_REGEX = r'\b(?<!/)(?<!=)(?P<case>[0-9]{8})\b'
KARMA_REGEX = r'\b(?P<nick>[a-zA-Z0-9_\-\[\]{}^`|]+)(?P<direction>\+\+|--)'
ESCALATION_URL = 'https://mojo.redhat.com/docs/DOC-1123528'
SNOW_URL = 'https://redhat.service-now.com/help?id=sc_cat_item&sys_id=200813d513e3f600dce03ff18144b0fd'
SNOW_SEARCH = 'https://redhat.service-now.com/surl.do?n='
SNOW_QUEUE = 'https://redhat.service-now.com/nav_to.do?uri=%2Fhome_splash.do%3Fsysparm_direct%3Dtrue'
SFDC_URL = 'https://access.redhat.com/support/cases/#/case/'


###############################################################
# Helping functions that support the bot's main functionality #
###############################################################
def debug(bot, message):
    """Provides debugging messages to bot owner if enabled."""
    if DEBUG:
        bot.say(message, bot.config.core.owner)

def announce_shift(bot, channel, rotation):
    """Anounces a shift and sets the topic to reflect that change"""
    debug(bot,
          'announce_shift_complete: shifts - curr:{s1}'.format(s1=rotation))

    hashline = formatting.color('###', formatting.colors.RED)
    lead = formatting.color('    Shift Lead: {curr_nick}'.format(curr_nick=rotation['Shift Lead']),
                            formatting.colors.RED)
    secondary = formatting.color('    Shift Secondary: {curr_nick}'.format(curr_nick=rotation['Shift Secondary']),
                                 formatting.colors.RED)
    oncall = formatting.color('    On-Call: {oncall_nick}'.format(oncall_nick=rotation['Oncall']),
                              formatting.colors.RED)
    oncallWeeday = formatting.color('    No oncall scheduled on weekdays, contact shift lead',
                              formatting.colors.RED)

    if bot.db.get_channel_value(channel, 'announce'):
        print("Annoucing to channel " + str(channel))
        bot.say(hashline, channel)
        bot.say(lead, channel)
        bot.say(secondary, channel)
        if rotation['Oncall']:
            bot.say(oncall, channel)
        else: 
            bot.say(oncallWeeday, channel)
    else:
        print("Failed to get channel value")

def set_topic_to_shift(bot, channel, rotation):
    """Sets topic to match the current shift information."""
    debug(bot,
          'setting channel topic: shifts - curr:{s1}'.format(s1=rotation))
    bot.write(
        ['TOPIC', channel],
        'Current Shift Lead: {lead} - Shift Secondary: {secondary} - OnCall: {oncall} - '.format(
            lead=rotation['Shift Lead'],
            secondary=rotation['Shift Secondary'],
            oncall=rotation['Oncall']))


def get_rotation():
    """This function gets the rotation from the pagerduty api"""
    pypd.api_key = os.environ['PAGER_DUTY_API_KEY']
    oncall = pypd.OnCall.find(escalation_policy_ids=["PA4586M"])
    escalation_level = { 1:'Shift Lead', 2:'Shift Secondary', 5: 'Oncall' }

    #print(json.dumps(escalation_level,indent=4,sort_keys=True))
    #print(oncall)
    
    # Set a rotation with default value of None , gets overwritten in the for loop if there an Oncall
    rotation ={
        'Oncall': None
    }

    for obj in oncall:
        esc_level = obj.get('escalation_level')
        if esc_level in escalation_level.keys():
            on_call_user = obj.get('user')
            user_name = on_call_user.get('summary')
            user = pypd.User.find_one(name=user_name)

            rotation[escalation_level[obj.get('escalation_level')]] = user.get('name')
            if user.get('description'):
                rotation[escalation_level[obj.get('escalation_level')]] = user.get('description')
            
    return rotation

def announce_escalation(bot, channel, rotation):
    """This function pulls  current rotation from  pagerduty api and checks it against a local version of the rotation.
    If it differs it announces the new rotation and sets the topic to reflect that change.
    If it does not find a file with current state it will announce the rotation it got from the pagerduty api"""
    SHIFT_FILE=str(channel) + ".json"
    stored_rotation = None
    try:
        stored_rotation = read_escalation_file(SHIFT_FILE)
    except IOError:
        print("No 'SHIFT_FILE' file found")
    finally:
        if stored_rotation != rotation:
            print("Annoucing Rotation")
            store_escalation(SHIFT_FILE, rotation)
            announce_shift(bot, channel, rotation)
            set_topic_to_shift(bot, channel, rotation)

def store_escalation(filename, rotation):
    """This function stores escalations in a json format to a file"""
    with open(filename, 'w') as outfile:
        json.dump(rotation, outfile)
    outfile.close()

def read_escalation_file(filename):
    """This function restores escalations from a file"""
    with open(filename) as json_file:
        rotation = json.load(json_file)
    json_file.close()
    return rotation

def get_msg_list(bot, channel):
    """Provides a uniform way of getting the msg_list from a channel db"""
    msg_list = bot.db.get_channel_value(channel, 'msg_list')
    if msg_list and isinstance(msg_list, list):
        debug(bot, 'List found: ' + str(msg_list))
        return msg_list
    else:
        debug(bot, 'No list found')
        return []


def display_karma(bot, channel, nick):
    """Provides a uniform way of displaying a given nick's karma."""
    karma = bot.db.get_nick_value(nick, 'karma')
    if karma:
        bot.say(nick + ' has {karma} karma.'.format(karma=karma), channel)
    else:
        bot.say(nick + ' does not have any karma.', channel)

################
# Bot commands #
################
@module.commands('track')
@module.example('.track')
def mark_channel_track_oncall(bot, trigger):
    """Begins tracking on-call and shift lead rotations."""
    bot.db.set_channel_value(trigger.sender, 'monitoring', True)
    bot.db.set_channel_value(trigger.sender, 'announce', True)
    bot.say(
        trigger.sender + ' is now tracking SRE on-call rotation')


@module.commands('untrack')
@module.require_admin('You must be a bot admin to use this command')
def unmark_channel_track_oncall(bot, trigger):
    """Stops tracking on-call and shift lead rotations for channel."""
    if bot.db.get_channel_value(trigger.sender, 'monitoring'):
        bot.db.set_channel_value(trigger.sender, 'monitoring', None)
        bot.db.set_channel_value(trigger.sender, 'announce', None)
        bot.say(trigger.sender + ' is no longer tracking SRE on-call rotations.')
    else:
        bot.say(trigger.sender + ' is not currently tracking SRE on-call rotations.')

@module.commands('shift-announce')
@module.require_admin('You must be a bot admin to use this command')
def mark_channel_announcements(bot, trigger):
    """Starts shift change announcements in channel if previously stopped."""
    if bot.db.get_channel_value(trigger.sender, 'monitoring'):
        if bot.db.get_channel_value(trigger.sender, 'announce'):
            bot.say('I\'m already announcing in this channel.')
        else:
            bot.db.set_channel_value(trigger.sender, 'announce', True)
            bot.say('I will resume announcements in this channel.')
    else:
        bot.say('I\'m not currently tracking this channel. Check out .help track')


@module.commands('shift-unannounce')
@module.require_admin('You must be a bot admin to use this command')
def unmark_channel_announcements(bot, trigger):
    """Stops shift change announcements in channel, while still allowing the other benefits of tracking
    the shift change schedule."""
    if bot.db.get_channel_value(trigger.sender, 'monitoring'):
        if bot.db.get_channel_value(trigger.sender, 'announce'):
            bot.db.set_channel_value(trigger.sender, 'announce', None)
            bot.say('I will no longer announce shift changes in this channel.')
            bot.say('Topic updates will still occur if I have the proper permissions.')
        else:
            bot.say('I\'m already not announcing in this channel.')
    else:
        bot.say('I\'m not currently tracking this channel. Check out .help track')


@module.commands('shift-update-topic')
def update_topic(bot, trigger):
    """Allows for force-updating a tracked channel's topic."""
    if bot.db.get_channel_value(trigger.sender, 'monitoring'):
        rotation = get_rotation()
        set_topic_to_shift(bot, trigger.sender, rotation)
    else:
        bot.say('I\'m not currently tracking this channel. Check out .help track')


@module.commands('shift')
def say_shift_leads(bot, trigger):
    """Lists the current on-call and shift leads for this rotation period."""
    if bot.db.get_channel_value(trigger.sender, 'monitoring'):
        rotation = get_rotation()
        announce_shift(bot, trigger.sender, rotation)
    else:
        bot.say(trigger.sender + ' is not currently tracking SRE on-call rotations.')


@module.commands('monitored-channels')
@module.require_admin('You must be a bot admin to use this command')
def say_monitored_channels_list(bot, trigger):
    """Sends PRIVMSG of all channels currently monitored for on-call and shift lead rotations.
    Will only respond to bot admins."""
    channels = 0
    for channel in bot.channels:
        if bot.db.get_channel_value(channel, 'monitoring'):
            bot.say(channel, trigger.nick)
            channels += 1
    if channels == 0:
        bot.say('No monitored channels.', trigger.nick)
    bot.say('I\'ve sent you a privmsg.')


@module.commands('snow')
def say_snow_ticket_url(bot, trigger):
    """Responds with the SNOW OpenShift SRE Service Request Form.
    https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form"""
    debug(bot, 'say_snow_ticket_url: using ' + trigger)
    bot.say(SNOW_URL)


@module.rule('^all:(.*)')
@module.commands('all')
@module.example('.all All users in this channel will be pinged on this message',
                '<nick1> <nick2> <nickN> Everyone that is a managed user will be pinged on this message')
def say_all(bot, trigger):
    """Will echo any text, with all channel users included in the message to ensure visibility."""
    if trigger.startswith('.all') and trigger.group(2):
        message = trigger.group(2)
    elif trigger.startswith('all:') and trigger.group(1):
        message = trigger.group(1)
    else:
        bot.say('If you don\'t have anything nice to say, then don\'t say anything at all.')
        return

    all_list = []
    for user, user_obj in bot.users.items():
        if user == bot.nick:
            continue
        if trigger.sender in user_obj.channels:
            debug(bot, 'Found user: {}'.format(user))
            all_list.append(user)
    if len(all_list) > 0:
        if not bot.db.get_nick_value(trigger.nick, 'all_warned'):
            bot.reply('Have you considered using the less noisy `.msg` option? '
                      'It will only notify specific users. Try `.msg-list` to see who would be notified.')
            bot.db.set_nick_value(trigger.nick, 'all_warned', True)
        bot.say(' '.join(all_list) + ': ' + message, max_messages=50)
    else:
        bot.reply('It\'s awfully lonely in here.')


@module.commands('msg')
@module.example('.msg Everyone that is a managed user will be pinged on this message',
                '<nick1> <nick2> <nickN> Everyone that is a managed user will be pinged on this message')
def say_msg(bot, trigger):
    """Will echo any text, with managed users included in the message to ensure visibility."""
    if trigger.group(2):
        msg_list = get_msg_list(bot, trigger.sender)
        if len(msg_list) > 0:
            bot.say(' '.join(msg_list) + ': ' + trigger.group(2), max_messages=50)
        else:
            bot.reply('I don\'t have any users to send to. Try having an admin use `.msg-add <nick>` to add someone.')
    else:
        bot.say('If you don\'t have anything nice to say, then don\'t say anything at all.')


@module.commands('msg-add')
@module.example('.msg-add <nick>')
@module.require_admin('You must be a bot admin to use this command')
def add_user_to_msg(bot, trigger):
    """Will add a user as a managed user for receiving .msg messages.
    Will only respond to bot admins."""
    if trigger.group(2):
        msg_list = get_msg_list(bot, trigger.sender)
        msg_list.append(trigger.group(2))
        bot.db.set_channel_value(trigger.sender, 'msg_list', msg_list)
        if len(msg_list) > 0:
            bot.say(trigger.group(2) + ' has been added to the .msg list.')
        else:
            bot.say('The .msg list has been initialized, and ' + trigger.group(2) + ' has been added.')
    else:
        bot.say('Don\'t forget to give me the nick to add to the .msg list.')


@module.commands('msg-delete')
@module.example('.msg-delete <nick>')
@module.require_admin('You must be a bot admin to use this command')
def delete_user_from_msg(bot, trigger):
    """Will delete a user from receiving .msg messages.
    Will only respond to bot admins."""
    if trigger.group(2):
        msg_list = get_msg_list(bot, trigger.sender)
        if len(msg_list) > 0 and trigger.group(2) in msg_list:
            msg_list.remove(trigger.group(2))
            bot.db.set_channel_value(trigger.sender, 'msg_list', msg_list)
            bot.say(trigger.group(2) + ' has been removed from the .msg list.')
        else:
            bot.say('That nick (' + trigger.group(2) + ') does not exist in the .msg list.')
    else:
        bot.say('Don\'t forget to give me the nick to remove from the .msg list.')


@module.commands('msg-deleteall')
@module.require_admin('You must be a bot admin to use this command')
def delete_all_users_from_msg(bot, trigger):
    """Deletes all users from receiving .msg messages.
    Will only respond to bot admins."""
    if trigger.group(2) == 'confirm':
        bot.db.set_channel_value(trigger.sender, 'msg_list', None)
        bot.say('I\'ve removed all users from the .msg list.')
    else:
        msg_list = get_msg_list(bot, trigger.sender)
        if len(msg_list) > 0:
            bot.say('This is a destructive command that will remove ' + str(len(msg_list)) +
                    ' users from the .msg list.')
            bot.reply('If you still want to do this, please run: .msg-deleteall confirm')
        else:
            bot.db.set_channel_value(trigger.sender, 'msg_list', None)
            bot.say('There are no users to delete.')


@module.commands('msg-list')
def say_msg_list(bot, trigger):
    """Provides the list of managed users that receive .msg messages"""
    msg_list = get_msg_list(bot, trigger.sender)
    if len(msg_list) > 0:
        bot.say('Check your PM')
        bot.say('.msg list users:', trigger.nick)
        bot.say(' '.join(msg_list), trigger.nick, max_messages=50)
    else:
        bot.say('There are no users in .msg list.')


@module.commands('admins')
@module.require_admin('You must be a bot admin to use this command')
def say_admin_list(bot, trigger):
    """Sends privmsg of all current admins.
    Will only respond to bot admins."""
    bot.say('Check your PM')
    bot.say('Current bot owner: ' + bot.config.core.owner, trigger.nick)
    admins = bot.config.core.admins
    if len(admins) > 0:
        bot.say('Current bot admins:', trigger.nick)
        for admin in admins.split(','):
            bot.say('\t' + admin, trigger.nick)
    else:
        bot.say('No configured admins', trigger.nick)
    bot.say('New admins can be added by creating a PR against '
            'https://github.com/openshift/openshift-ansible-ops/tree/prod/playbooks/adhoc/ircbot', trigger.nick)


@module.commands('karma')
@module.example('.karma', 'You have X karma')
@module.example('.karma <nick>', '<nick> has X karma')
def say_karma(bot, trigger):
    """List karma of yourself or a given nick"""
    if trigger.group(2):
        for nick in trigger.group(2).split():
            display_karma(bot, trigger.sender, nick)
    else:
        display_karma(bot, trigger.sender, trigger.nick)


#################
# Bot intervals #
#################
# Update every 5 minutes
@module.interval(300)
# Testing Intervals 
#@module.interval(15)
def track_shift_rotation(bot):
    """ Sends a message if there was a change in the rotation withnin the last 10 minutes
    (if bot has appropriate channel permissions)."""

    print("Checking shift rotation " + str(datetime.datetime.utcnow()))
    rotation = get_rotation()

    for channel in bot.channels:
        if bot.db.get_channel_value(channel, 'monitoring'):
            announce_escalation(bot, channel, rotation)


######################
# Bot regex matching #
######################
@module.rule(r'.*')
@module.priority('high')
def refer_to_topic(bot, trigger):
    """If any 'monitored channels' are mentioned in their own channel, refer the user to shift-lead or on-call user."""
    if bot.db.get_channel_value(trigger.sender, 'monitoring') and str(trigger.sender)[1:] in str(trigger):
        bot.say('Please reach out to the shift lead or on-call SRE')
        say_shift_leads(bot, trigger)

@module.rule(r'(.*)')
def snow_ticket(bot, trigger):
    """Provides the SNOW ticket URL."""
    tickets = []
    for service_ticket in finditer(SNOW_TICKET_REGEX, trigger):
        tickets.append(service_ticket.groupdict()['ticket'])
    if len(tickets) > 0:
        for ticket in tickets:
            bot.say(SNOW_SEARCH + ticket)


@module.rule(r'(.*)')
def sfdc_case(bot, trigger):
    """Reminds users that SFDC cases require a matching SNOW ticket, and also provide the SFDC URL."""
    cases = []
    for support_case in finditer(SFDC_CASE_REGEX, trigger):
        cases.append(support_case.groupdict()['case'])
    if len(cases) > 0:
        for case in cases:
            bot.say(SFDC_URL + case)


@module.priority('high')
@module.rule(r'(.*)')
@module.example('<nick>++', '<nick> has X karma')
@module.example('<nick>--', '<nick> has X karma')
def apply_karma(bot, trigger):
    """Adds or removes karma from a given nick. Karma extends to all channels the bot exists in."""
    for karma_match in finditer(KARMA_REGEX, trigger):
        karma = karma_match.groupdict()
        if karma['nick'] == trigger.nick:
            bot.say('You can\'t change your own karma.')
            return
        debug(bot, 'Applying karma to {nick} in direction {direction}'.format(nick=karma['nick'],
                                                                              direction=karma['direction']))
        karma_amt = 1 if karma['direction'] == '++' else -1
        curr_karma = bot.db.get_nick_value(karma['nick'], 'karma')
        if curr_karma is None:
            curr_karma = 0
        bot.db.set_nick_value(karma['nick'], 'karma', curr_karma + karma_amt)
        bot.say(karma['nick'] + ' now has {karma} karma.'.format(karma=(curr_karma + karma_amt)))
