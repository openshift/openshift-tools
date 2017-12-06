# coding=utf-8
# pylint: disable=protected-access
# pylint: disable=import-error
"""
openshift_sre.py - Various helper modules for OpenShift Online SRE team
Copyright © 2017, Will Gordon <wgordon@redhat.com>
Licensed under the MIT license.
"""
from __future__ import print_function
from datetime import datetime as dt
from re import finditer, search
from sopel import module
from sopel.config.types import StaticSection, FilenameAttribute
from pygsheets import authorize, exceptions
from pytz import timezone
from googleapiclient import errors

###########################
# Configuration constants #
###########################
DEBUG = False  # Debug sends debug messages to the bot owner via PRIVMSG
GSHEET_URL_REGEX = r'https://docs\.google\.com/spreadsheets/d/(?P<key>[a-zA-Z0-9_\-]*)/edit#gid=(?P<gid>[0-9]*)'
SNOW_TICKET_REGEX = r'\b(?<!=)(?P<ticket>(TASK|REQ|RITM|INC|PRB|CHG)[0-9]{7})\b'
SFDC_CASE_REGEX = r'\b(?<!/)(?<!=)(?P<case>[0-9]{8})\b'
KARMA_REGEX = r'\b(?P<nick>[a-zA-Z0-9_\-\[\]{}^`|]+)(?P<direction>\+\+|--)'
ESCALATION_URL = 'https://mojo.redhat.com/docs/DOC-1123528'
SNOW_URL = 'https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form'
SNOW_SEARCH = 'https://redhat.service-now.com/surl.do?n='
SNOW_QUEUE = 'https://redhat.service-now.com/nav_to.do?uri=%2Fhome_splash.do%3Fsysparm_direct%3Dtrue'
SFDC_URL = 'https://gss.my.salesforce.com/apex/Case_View?sbstr='
# Schedules taken from https://mojo.redhat.com/docs/DOC-1144371 and localized
# New, proposed schedule: https://docs.google.com/document/d/13UGqePqjsEzUqupTat8XgJDKALb0WQ3lP66OYfk6cO0/edit
# TZ Compare:
#   https://www.timeanddate.com/worldclock/converter.html?iso=20171121T050000&p1=1440&p2=47&p3=237&p4=204&p5=207
# DST lookup: https://www.timeanddate.com/time/change/usa/raleigh,
#             https://www.timeanddate.com/time/change/czech-republic/brno
APAC_1 = {
    'name': 'Brisbane',
    'column': '?',
    'start_1': 9,
    'start_2': 9,
    'start_3': 8,
    'start_4': 9,
    'tz': timezone('Australia/Brisbane')
}
APAC_2 = {
    'name': 'Beijing',
    'column': 'O',
    'start_1': 7,
    'start_2': 7,
    'start_3': 6,
    'start_4': 7,
    'tz': timezone('Asia/Shanghai')
}
EMEA = {
    'name': 'EMEA',
    'column': 'M',
    'start_1': 8,
    'start_2': 8,
    'start_3': 8,
    'start_4': 8,
    'tz': timezone('Europe/Prague')
}
NASA = {
    'name': 'NASA',
    'column': 'K',
    'start_1': 10,
    'start_2': 11,
    'start_3': 10,
    'start_4': 11,
    'tz': timezone('US/Eastern')
}
ONCALL = {
    'name': 'ONCALL',
    'column': 'C'
}
# DST schedule to follow for start times
# MUST be ordered
STARTS = [
    # start_1 begins at the end of NASA DST
    [transition for transition in NASA['tz']._utc_transition_times if transition.year == dt.utcnow().year][1],
    # start_2 beings at the start of NASA DST
    [transition for transition in NASA['tz']._utc_transition_times if transition.year == dt.utcnow().year][0],
    # start_3 beings at the start of EMEA DST
    [transition for transition in EMEA['tz']._utc_transition_times if transition.year == dt.utcnow().year][0],
    # start_4 begins at the end of EMEA DST
    [transition for transition in EMEA['tz']._utc_transition_times if transition.year == dt.utcnow().year][1]
]
# Ordered list of shifts, i.e., APAC is the first shift of a given day and NASA is the last shift
# SHIFTS = [APAC_1, APAC_2, EMEA, NASA]
SHIFTS = [APAC_2, EMEA, NASA]
# Specify the time and date for when a new shift period should be used
SHIFT_CHANGE = {
    'hour': 11,
    'tz': NASA['tz']
}
START_ANNOUNCING = {
    'tz': APAC_1['tz'],
    'weekday': 0,
    'hour': 8
}
STOP_ANNOUNCING = {
    'tz': NASA['tz'],
    'weekday': 4,
    'hour': 17
}


##############################
# Configuration file section #
###############################
class SreSection(StaticSection):
    """Defines the config section for OpenShift SRE"""
    google_service_account_file = FilenameAttribute('google_service_account_file',
                                                    directory=False,
                                                    default='service_account.json')
    """File generated from a Google Cloud project (https://console.developers.google.com).

    In a project, generate a service_account file from
    APIs & services > Credentials > Create credentials > Service account key.
    Also, be sure to enable Google Drive API.
    """


def configure(config):
    """Adds SreSection to config"""
    config.define_section('openshift_sre', SreSection)
    config.openshift_sre.configure_setting(
        'google_service_account_file',
        'Enter the path to your service_account.json file.'
    )


def setup(bot):
    """Sets up config with defaults in the case of missing SreSection"""
    bot.config.define_section('openshift_sre', SreSection)


###############################################################
# Helping functions that support the bot's main functionality #
###############################################################
def debug(bot, message):
    """Provides debugging messages to bot owner if enabled."""
    if DEBUG:
        bot.say(message, bot.config.core.owner)


def read_google_sheet(bot, gsheet_url, channel):
    """Parses a google sheet URL."""
    if gsheet_url:
        match = search(GSHEET_URL_REGEX, gsheet_url)
        groups = match.groupdict()
        try:
            gsheet_client = authorize(service_file=bot.config.openshift_sre.google_service_account_file)
        except ValueError:
            bot.say('The Service Account JSON file doesn\'t appear to exist. See '
                    'https://cloud.google.com/storage/docs/authentication#service_accounts for creating a service '
                    'account. Then move to ' + bot.config.openshift_sre.google_service_account_file, channel,
                    max_messages=50)
            return
        except exceptions.RequestError:
            bot.say('Sorry, I timed-out trying to access the on-call schedule. Please try that again.', channel)
            return
        # Open Spreadsheet for access
        try:
            sheet = gsheet_client.open_by_key(groups['key'])
        except errors.HttpError as err:
            if err.resp['status'] in ['403', '404']:
                bot.say(
                    'I can\'t seem to access that spreadsheet ({url}). Are you sure that the URL is correct and that '
                    '{service_account_email} has been invited to that doc?'.format(
                        url=gsheet_url,
                        service_account_email=gsheet_client.oauth.service_account_email), channel, max_messages=50)
            else:
                bot.say('Unknown error: ' + str(err), channel, max_messages=50)
            return
        else:
            # Find worksheet based on `gid` in URL
            for worksheet in sheet.worksheets():
                if str(worksheet.id) == groups['gid']:
                    current_worksheet = worksheet
                    break
            else:
                bot.say('The worksheet (gid={gid}) on that spreadsheet ({title}) doesn\'t seem to exist.'.format(
                    gid=groups['gid'],
                    title=sheet.title), channel)
                return
            return current_worksheet
    else:
        bot.say('A valid Google Sheet URL was not provided', channel)
        return


def announce_shift_preparing(bot, channel):
    """Must be called *before* the shift change 'hour'."""
    prev_shift, curr_shift, next_shift = get_shift(bot)
    debug(bot, 'announce_shift_preparing: shifts - prev:{s1} - curr:{s2} - next:{s3}'.format(s1=prev_shift['name'],
                                                                                             s2=curr_shift['name'],
                                                                                             s3=next_shift['name']))
    leads = get_shift_leads(bot, channel)
    if bot.db.get_channel_value(channel, 'announce'):
        bot.say('{curr_shift} preparing to sign off, {next_shift} preparing to take over the environment'.format(
            curr_shift=curr_shift['name'], next_shift=next_shift['name']), channel)
        bot.say('{curr_nick}: What happened today? What does {next_nick} need to know about?'.format(
            curr_nick=leads[curr_shift['name']], next_nick=leads[next_shift['name']]), channel)
        bot.say('Check SNOW ticket queue here {queue}'.format(queue=SNOW_QUEUE), channel)


def announce_shift_complete(bot, channel):
    """Must be called *after* the shift change 'hour'."""
    prev_shift, curr_shift, next_shift = get_shift(bot)
    debug(bot,
          'announce_shift_complete: shifts - prev:{s1} - curr:{s2} - next:{s3} '.format(
              s1=prev_shift['name'], s2=curr_shift['name'], s3=next_shift['name']))
    leads = get_shift_leads(bot, channel)
    if bot.db.get_channel_value(channel, 'announce'):
        bot.say('Shift change complete', channel)
        bot.say('Shift Lead: {curr_nick}'.format(curr_nick=leads[curr_shift['name']]), channel)
        bot.say('On-Call: {oncall_nick}'.format(oncall_nick=leads[ONCALL['name']]), channel)
        bot.say('Thanks {prev_shift}, enjoy your evening!'.format(prev_shift=prev_shift['name']), channel)


def set_topic_to_shift(bot, channel):
    """Sets topic to match the current shift information."""
    prev_shift, curr_shift, next_shift = get_shift(bot)
    debug(bot,
          'announce_shift_complete: shifts - prev:{s1} - curr:{s2} - next:{s3} '.format(
              s1=prev_shift['name'], s2=curr_shift['name'], s3=next_shift['name']))
    leads = get_shift_leads(bot, channel)
    bot.write(
        ['TOPIC', channel],
        'Current Shift Lead: {lead} - OnCall: {oncall} - '
        'Shift Change at: Beijing - {beijing:%H:00}; Brno - {brno:%H:00}; Raleigh - {raleigh:%H:00}'.format(
            lead=leads[curr_shift['name']],
            oncall=leads[ONCALL['name']],
            beijing=dt.now(next_shift['tz']).replace(hour=next_shift[get_shift_start(bot)]),
            brno=dt.now(next_shift['tz']).replace(hour=next_shift[get_shift_start(bot)]),
            raleigh=dt.now(next_shift['tz']).replace(hour=next_shift[get_shift_start(bot)])))


def get_shift(bot):
    """Shift changes occur on their specified hour."""
    for i, shift in enumerate(SHIFTS):
        now = dt.now(shift['tz'])
        if shift[get_shift_start(bot)] <= now.hour < (shift[get_shift_start(bot)] + 8):
            prev_shift = SHIFTS[(i - 1) % len(SHIFTS)]
            curr_shift = SHIFTS[i % len(SHIFTS)]
            next_shift = SHIFTS[(i + 1) % len(SHIFTS)]
            break
    else:
        raise ValueError('No shift defined for ' + str(dt.utcnow().isoformat()))
    return prev_shift, curr_shift, next_shift


def get_shift_start(bot):
    """Determines which schedule start time to used based on DST dates"""
    now = dt.utcnow()
    # now = bot  # Used during local testing
    for i, dst_date in enumerate(STARTS):
        if dst_date == max(STARTS) and dst_date <= now <= dt(dst_date.year, 12, 31):
            return 'start_' + str(i + 1)
        elif dst_date == min(STARTS) and dt(dst_date.year, 1, 1) <= now < dst_date:
            return 'start_' + str(i)
        elif dst_date <= now < (STARTS[(i + 1) % len(STARTS)]):
            return 'start_' + str(i + 1)
    debug(bot, 'Unable to determine the shift_start for date: {}'.format(now))


def get_shift_leads(bot, channel):
    """Finds the row from provided oncall g-sheet, and returns a Dict of IRC nicks."""
    worksheet = read_google_sheet(bot, bot.db.get_channel_value(channel, 'monitoring'), channel)
    now = dt.now(SHIFT_CHANGE['tz'])
    if worksheet:
        row = 0
        for index, period in enumerate(worksheet.get_col(2)):
            try:
                period_dt = dt.strptime(period, '%m/%d/%y')
            except ValueError:
                pass
            else:
                if period_dt.date() >= now.date():
                    # New shift period occurs on Friday at 11am EST
                    if period_dt.date() == now.date() and now.hour >= SHIFT_CHANGE['hour']:
                        row = index + 1
                        debug(bot, 'get_shift_leads: After shift change, using new period ({period})'.format(
                            period=period_dt.date()))
                    else:
                        row = index
                        debug(bot, 'get_shift_leads: Using period ({period})'.format(period=period_dt.date()))
                    break
        if row > 0:
            shift_leads = {
                NASA['name']: worksheet.cell(str(NASA['column'] + str(row))).value,
                EMEA['name']: worksheet.cell(str(EMEA['column'] + str(row))).value,
                APAC_2['name']: worksheet.cell(str(APAC_2['column'] + str(row))).value,
                ONCALL['name']: worksheet.cell(str(ONCALL['column'] + str(row))).value
            }
            debug(bot, 'get_shift_leads: Found leads - {leads}'.format(leads=shift_leads))
            return shift_leads
    bot.say('Unable to find shift leads for ' + str(
        now.isoformat()) + '. Currently tracking shift from ' + bot.db.get_channel_value(channel, 'monitoring'),
            channel)
    return {}


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
@module.example(
    '.track https://docs.google.com/spreadsheets/d/1oDSiUaS3MijjQxygc6kgJCtcOKWi67EZWF02qSAgoZw/edit#gid=1539275069')
def mark_channel_to_track_oncall(bot, trigger):
    """Begins tracking on-call and shift lead rotations from a provided google spreadsheet.
    Can also list the currently tracked URL"""
    if trigger.group(2):
        worksheet = read_google_sheet(bot, trigger.group(2), trigger.sender)
        if worksheet:
            bot.db.set_channel_value(trigger.sender, 'monitoring', trigger.group(2))
            bot.db.set_channel_value(trigger.sender, 'announce', True)
            bot.say(
                trigger.sender + ' is now tracking SRE on-call rotation: ' + bot.db.get_channel_value(trigger.sender,
                                                                                                      'monitoring'))
    else:
        gsheet_url = bot.db.get_channel_value(trigger.sender, 'monitoring')
        if gsheet_url:
            bot.say('Currently tracking SRE on-call rotations from ' + gsheet_url)
        else:
            bot.say('Not currently tracking an SRE on-call rotation.')


@module.commands('untrack')
def unmark_channel_to_track_oncall(bot, trigger):
    """Stops tracking on-call and shift lead rotations for channel."""
    if bot.db.get_channel_value(trigger.sender, 'monitoring'):
        bot.db.set_channel_value(trigger.sender, 'monitoring', None)
        bot.db.set_channel_value(trigger.sender, 'announce', None)
        bot.say(trigger.sender + ' is no longer tracking SRE on-call rotations.')
    else:
        bot.say(trigger.sender + ' is not currently tracking SRE on-call rotations.')


@module.commands('shift-announce')
def mark_channel_for_announcements(bot, trigger):
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
def unmark_channel_for_announcements(bot, trigger):
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


@module.commands('shift')
def say_shift_leads(bot, trigger):
    """Lists the current on-call and shift leads for this rotation period."""
    if bot.db.get_channel_value(trigger.sender, 'monitoring'):
        for shift, lead in get_shift_leads(bot, trigger.sender).items():
            bot.say(str(shift) + ': ' + str(lead))
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
# Update every 10 minutes
@module.interval(600)
def track_shift_rotation(bot):
    """Sends appropriate message ~10 minutes before and ~15 minutes after shift changes and sets channel topic
    (if bot has appropriate channel permissions).
    Does not send announcements over weekends."""
    for channel in bot.channels:
        if bot.db.get_channel_value(channel, 'monitoring'):
            start_now = dt.now(tz=START_ANNOUNCING['tz'])
            stop_now = dt.now(tz=STOP_ANNOUNCING['tz'])
            if (start_now.weekday() > START_ANNOUNCING['weekday'] and stop_now.weekday() < STOP_ANNOUNCING[
                    'weekday']) or \
                    (start_now.hour >= START_ANNOUNCING['hour'] and start_now.weekday() == START_ANNOUNCING[
                        'weekday']) or \
                    (stop_now.hour <= STOP_ANNOUNCING['hour'] and stop_now.weekday() == STOP_ANNOUNCING['weekday']):
                _, curr_shift, next_shift = get_shift(bot)
                curr_now = dt.now(curr_shift['tz'])
                next_now = dt.now(next_shift['tz'])
                # Shift prepares to end between (start-1):50 and (start-1):59
                if next_now.hour == (next_shift[get_shift_start(bot)] - 1) and 50 <= next_now.minute <= 59:
                    announce_shift_preparing(bot, channel)
                # Shift ends between (start):10 and (start):19
                elif curr_now.hour == curr_shift[get_shift_start(bot)] and 10 <= curr_now.minute <= 19:
                    announce_shift_complete(bot, channel)
                    set_topic_to_shift(bot, channel)
            else:
                debug(bot, 'Ignoring messaging due to weekend hours')


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


@module.rule(r'.*')
@module.rate(channel=600)
def monitor_weekend(bot, trigger):
    """Reminds users that channels are un-monitored on weekends. Will not trigger more than once every 10 minutes."""
    if bot.db.get_channel_value(trigger.sender, 'monitoring') and dt.utcnow().weekday() > 4:
        bot.reply('This channel is unmonitored on weekends. See {url} for Engineer Escalations.'.format(
            url=ESCALATION_URL))


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


if __name__ == '__main__':
    # Tests DST start schedules
    # Based on 2017 DST dates, requires changing `now = dt.utcnow()` to `now = bot` in get_shift_start()
    STARTS = [
        # start_1 begins at the end of NASA DST
        [transition for transition in NASA['tz']._utc_transition_times if transition.year == 2017][1],
        # start_2 beings at the start of NASA DST
        [transition for transition in NASA['tz']._utc_transition_times if transition.year == 2017][0],
        # start_3 beings at the start of EMEA DST
        [transition for transition in EMEA['tz']._utc_transition_times if transition.year == 2017][0],
        # start_4 begins at the end of EMEA DST
        [transition for transition in EMEA['tz']._utc_transition_times if transition.year == 2017][1]
    ]

    assert get_shift_start(dt(2017, 12, 31)) == 'start_1', 'Found {} instead'.format(get_shift_start(dt(2017, 12, 31)))
    assert get_shift_start(dt(2017, 1, 1)) == 'start_1', 'Found {} instead'.format(get_shift_start(dt(2017, 1, 1)))
    assert get_shift_start(dt(2017, 2, 1)) == 'start_1', 'Found {} instead'.format(get_shift_start(dt(2017, 2, 1)))
    assert get_shift_start(dt(2017, 3, 1)) == 'start_1', 'Found {} instead'.format(get_shift_start(dt(2017, 3, 1)))
    assert get_shift_start(dt(2017, 3, 11)) == 'start_1', 'Found {} instead'.format(get_shift_start(dt(2017, 3, 11)))
    assert get_shift_start(dt(2017, 3, 12)) == 'start_1', 'Found {} instead'.format(get_shift_start(dt(2017, 3, 12)))
    assert get_shift_start(dt(2017, 3, 13)) == 'start_2', 'Found {} instead'.format(get_shift_start(dt(2017, 3, 13)))
    assert get_shift_start(dt(2017, 3, 12, 10, 0)) == 'start_2', 'Found {} instead'.format(
        get_shift_start(dt(2017, 3, 12, 10, 0)))
    assert get_shift_start(dt(2017, 4, 12, 10, 0)) == 'start_3', 'Found {} instead'.format(
        get_shift_start(dt(2017, 4, 12, 10, 0)))
    assert get_shift_start(dt(2017, 3, 25, 10, 0)) == 'start_2', 'Found {} instead'.format(
        get_shift_start(dt(2017, 3, 25, 10, 0)))
    assert get_shift_start(dt(2017, 3, 26, 10, 0)) == 'start_3', 'Found {} instead'.format(
        get_shift_start(dt(2017, 3, 26, 10, 0)))
    assert get_shift_start(dt(2017, 10, 1, 10, 0)) == 'start_3', 'Found {} instead'.format(
        get_shift_start(dt(2017, 10, 1, 10, 0)))
    assert get_shift_start(dt(2017, 10, 28, 10, 0)) == 'start_3', 'Found {} instead'.format(
        get_shift_start(dt(2017, 10, 28, 10, 0)))
    assert get_shift_start(dt(2017, 10, 29, 10, 0)) == 'start_4', 'Found {} instead'.format(
        get_shift_start(dt(2017, 10, 29, 10, 0)))
    assert get_shift_start(dt(2017, 10, 30, 10, 0)) == 'start_4', 'Found {} instead'.format(
        get_shift_start(dt(2017, 10, 29, 10, 0)))
    assert get_shift_start(dt(2017, 11, 4, 10, 0)) == 'start_4', 'Found {} instead'.format(
        get_shift_start(dt(2017, 10, 29, 10, 0)))
    assert get_shift_start(dt(2017, 11, 5, 10, 0)) == 'start_1', 'Found {} instead'.format(
        get_shift_start(dt(2017, 10, 29, 10, 0)))
    assert get_shift_start(dt(2017, 11, 29, 10, 0)) == 'start_1', 'Found {} instead'.format(
        get_shift_start(dt(2017, 10, 29, 10, 0)))
    print('All tests pass')
