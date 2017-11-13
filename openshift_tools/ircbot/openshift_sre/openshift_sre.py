# coding=utf-8
"""
openshift_sre.py - Various helper modules for OpenShift Online SRE team
Copyright © 2017, Will Gordon <wgordon@redhat.com>
Licensed under the MIT license.
"""
import re
from datetime import datetime as dt
from sopel import module  # pylint: disable=import-error
from sopel.config.types import StaticSection, FilenameAttribute  # pylint: disable=import-error
from pygsheets import authorize  # pylint: disable=import-error
from pytz import timezone, utc  # pylint: disable=import-error
from googleapiclient import errors

DEBUG = False  # Debug sends debug messages to the bot owner via PRIVMSG
GSHEET_URL_REGEX = r'https://docs\.google\.com/spreadsheets/d/(?P<key>[a-zA-Z0-9_-]*)/edit#gid=(?P<gid>[0-9]*)'
SNOW_TICKET_REGEX = r'.*(?P<ticket>(TASK|REQ|RITM|INC|PRB|CHG)[0-9]{7}).*'
MONITORED_CHANNELS = []
ESCALATION_URL = 'https://mojo.redhat.com/docs/DOC-1123528'
SNOW_URL = 'https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form'
SNOW_SEARCH = 'https://redhat.service-now.com/surl.do?n='
SNOW_QUEUE = 'https://redhat.service-now.com/nav_to.do?uri=%2Fhome_splash.do%3Fsysparm_direct%3Dtrue'
APAC = {
    'name': 'APAC',
    'column': 'O',
    'utc_start': 22,
    'utc_end': 6
}
EMEA = {
    'name': 'EMEA',
    'column': 'M',
    'utc_start': 6,
    'utc_end': 14
}
NASA = {
    'name': 'NASA',
    'column': 'K',
    'utc_start': 14,
    'utc–end': 22
}
ONCALL = {
    'name': 'ONCALL',
    'column': 'C'
}
# Ordered list of shifts, i.e., APAC is the first shift of a given day and NASA is the last shift
SHIFTS = [APAC, EMEA, NASA]
# Specify the time and date for when a new shift period should be used
SHIFT_CHANGE = {
    'weekday': 4,
    'hour': 11,
    'tz': timezone('US/Eastern')
}


class SreSection(StaticSection):  # pylint disable=too-few-public-methods
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


def debug(bot, message):
    """Provides debugging messages to bot owner if enabled."""
    if DEBUG:
        bot.say(message, bot.config.core.owner)


def read_google_sheet(bot, gsheet_url, channel):
    """Parses a google sheet URL."""
    if gsheet_url:
        match = re.search(GSHEET_URL_REGEX, gsheet_url)
        groups = match.groupdict()
        try:
            gsheet_client = authorize(service_file=bot.config.openshift_sre.google_service_account_file)
        except ValueError:
            bot.say('The Service Account JSON file doesn\'t appear to exist. See '
                    'https://cloud.google.com/storage/docs/authentication#service_accounts for creating a service '
                    'account. Then move to ' + bot.config.openshift_sre.google_service_account_file, channel)
            return
        # Open Spreadsheet for access
        try:
            sheet = gsheet_client.open_by_key(groups['key'])
        except errors.HttpError as err:
            if err.resp['status'] == '403':
                bot.say(
                    'I don\'t have access to that spreadsheet({url}). Are you sure '
                    '{service_account_email} has been invited to that doc?'.format(
                        url=gsheet_url,
                        service_account_email=gsheet_client.oauth.service_account_email), channel)
            elif err.resp['status'] == '404':
                bot.say('That spreadsheet ({url}) doesn\'t appear to be correct as I\'m getting a 404 for that.'.format(
                    url=gsheet_url))
            else:
                bot.msg(channel, 'Unknown error: ' + str(err))
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


def announce_shift_preparing(bot, channel):
    """Must be called *before* the shift change 'hour'."""
    prev_shift, curr_shift, next_shift = get_shift(bot)
    debug(bot, 'announce_shift_preparing: shifts - prev:{s1} - curr:{s2} - next:{s3}'.format(s1=prev_shift['name'],
                                                                                             s2=curr_shift['name'],
                                                                                             s3=next_shift['name']))
    leads = get_shift_leads(bot, channel)
    bot.say('{curr_shift} preparing to sign off, {next_shift} preparing to take over the environment'.format(
        curr_shift=curr_shift['name'], next_shift=next_shift['name']), channel)
    bot.say('{curr_nick}: What happened today? What does {next_nick} need to know about?'.format(
        curr_nick=leads[curr_shift['name']], next_nick=leads[next_shift['name']]), channel)
    bot.say('Check SNOW ticket queue here {queue}'.format(queue=SNOW_QUEUE), channel)


def announce_shift_complete(bot, channel):
    """Must be called *after* the shift change 'hour'."""
    curr_shift, next_shift, prev_shift = get_shift(bot)
    debug(bot,
          'announce_shift_complete: shifts - prev:{s1} - curr:{s2} - next:{s3} '
          '(NOTE: shifts have been rearranged to match previous shift info)'.format(
              s1=prev_shift['name'], s2=curr_shift['name'], s3=next_shift['name']))
    leads = get_shift_leads(bot, channel)
    bot.say('Shift change complete', channel)
    bot.say('Shift Lead: {curr_nick}'.format(curr_nick=leads[curr_shift['name']]), channel)
    bot.say('On-Call: {oncall_nick}'.format(oncall_nick=leads[ONCALL['name']]), channel)
    bot.say('Thanks {prev_shift}, enjoy your evening!'.format(prev_shift=prev_shift['name']), channel)


def set_topic_to_shift(bot, channel):
    """Sets topic to match the current shift information."""
    prev_shift, curr_shift, next_shift = get_shift(bot)
    debug(bot,
          'announce_shift_complete: shifts - prev:{s1} - curr:{s2} - next:{s3} '
          '(NOTE: shifts have been rearranged to match previous shift info)'.format(
              s1=prev_shift['name'], s2=curr_shift['name'], s3=next_shift['name']))
    leads = get_shift_leads(bot, channel)
    bot.write(
        ['TOPIC', channel],
        'Current Shift Lead: {lead} - OnCall: {oncall} - '
        'Shift Change at: {next_shift_change}:00UTC (Brisbane - {brisbane:%H:00}; '
        'Beijing - {beijing:%H:00}; Brno - {brno:%H:00}; Raleigh - {raleigh:%H:00}'.format(
            lead=leads[curr_shift['name']],
            oncall=leads[ONCALL['name']],
            next_shift_change=next_shift['utc_start'],
            brisbane=dt.utcnow().replace(hour=next_shift['utc_start'], tzinfo=utc).astimezone(
                timezone('Australia/Brisbane')),
            beijing=dt.utcnow().replace(hour=next_shift['utc_start'], tzinfo=utc).astimezone(timezone('Asia/Shanghai')),
            brno=dt.utcnow().replace(hour=next_shift['utc_start'], tzinfo=utc).astimezone(timezone('Europe/Prague')),
            raleigh=dt.utcnow().replace(hour=next_shift['utc_start'], tzinfo=utc).astimezone(timezone('US/Eastern'))))


def get_shift(bot):
    """Shift changes occur on their specified hour."""
    now = dt.utcnow()
    for i, shift in enumerate(SHIFTS):
        if shift['utc_start'] > shift['utc_end']:
            if shift['utc_start'] <= now.hour <= 23 or 0 <= now.hour < shift['utc_end']:
                debug(bot, 'get_shift: Shift occurs overnight UCT')
                prev_shift = SHIFTS[i - 1 % len(SHIFTS)]
                curr_shift = SHIFTS[i % len(SHIFTS)]
                next_shift = SHIFTS[i + 1 % len(SHIFTS)]
                break
        else:
            if shift['utc_start'] <= now.hour < shift['utc_end']:
                prev_shift = SHIFTS[i - 1 % len(SHIFTS)]
                curr_shift = SHIFTS[i % len(SHIFTS)]
                next_shift = SHIFTS[i + 1 % len(SHIFTS)]
                break
    else:
        raise ValueError('No shift defined for ' + str(now.isoformat()))
    return prev_shift, curr_shift, next_shift


def get_shift_leads(bot, channel):
    """Finds the row from provided oncall g-sheet, and returns a Dict of IRC nicks."""
    worksheet = read_google_sheet(bot, bot.db.get_channel_value(channel, 'oncall'), channel)
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
                    if now.weekday() >= SHIFT_CHANGE['weekday'] and now.hour >= SHIFT_CHANGE['hour']:
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
                APAC['name']: worksheet.cell(str(APAC['column'] + str(row))).value,
                ONCALL['name']: worksheet.cell(str(ONCALL['column'] + str(row))).value
            }
            debug(bot, 'get_shift_leads: Found leads - {leads}'.format(leads=shift_leads))
            return shift_leads
    bot.say('Unable to find shift leads for ' + str(
        now.isoformat()) + '. Currently tracking shift from ' + bot.db.get_channel_value(channel, 'oncall'), channel)
    return {}


@module.commands('track')
@module.example(
    '.track https://docs.google.com/spreadsheets/d/1oDSiUaS3MijjQxygc6kgJCtcOKWi67EZWF02qSAgoZw/edit#gid=1539275069')
def mark_channel_to_track_oncall(bot, trigger):
    """Begins tracking on-call and shift lead rotations from a provided google spreadsheet."""
    worksheet = read_google_sheet(bot, bot.db.get_channel_value(trigger.sender, 'oncall'), trigger.sender)
    if worksheet:
        MONITORED_CHANNELS.append(trigger.sender)
        bot.db.set_channel_value(trigger.sender, 'oncall', trigger.group(2))
        bot.say(trigger.sender + ' is now tracking SRE on-call rotation: ' + bot.db.get_channel_value(trigger.sender,
                                                                                                      'oncall'))
    else:
        bot.say('Unable to track ' + trigger.group(2))


@module.commands('untrack')
def unmark_channel_to_track_oncall(bot, trigger):
    """Stops tracking on-call and shift lead rotations for channel."""
    try:
        MONITORED_CHANNELS.remove(trigger.sender)
    except ValueError:
        bot.say(trigger.sender + ' is not currently tracking SRE on-call rotations')
    else:
        bot.db.set_channel_value(trigger.sender, 'oncall', None)
        bot.say(trigger.sender + ' is no longer tracking SRE on-call rotations')


@module.commands('shift')
def say_shift_leads(bot, trigger):
    """Lists the current on-call and shift leads for this rotation period."""
    if trigger.sender in MONITORED_CHANNELS:
        for shift, lead in get_shift_leads(bot, trigger.sender).items():
            bot.say(str(shift) + ': ' + str(lead))
    else:
        bot.say(trigger.sender + ' is not currently tracking SRE on-call rotations')


@module.commands('monitored-channels')
@module.require_admin('You must be a bot admin to use this command')
def list_monitored_channels(bot, trigger):
    """Sends PRIVMSG of all channels currently monitored for on-call and shift lead rotations.
    Will only respond to bot admins."""
    if len(MONITORED_CHANNELS) > 0:
        for channel in MONITORED_CHANNELS:
            bot.say(channel, trigger.nick)
    else:
        bot.say('No monitored channels', trigger.nick)
    bot.say('Check your PM')


@module.commands('snow')
def say_snow_ticket_url(bot, trigger):
    """Responds with the SNOW OpenShift SRE Service Request Form
    https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form"""
    debug(bot, 'say_snow_ticket_url: using ' + trigger)
    bot.say(SNOW_URL)


# Update every 10 minutes
@module.interval(600)
def track_shift_rotation(bot):
    """Sends appropriate message ~10 minutes before and ~15 minutes after shift changes and sets channel topic
    (if bot has appropriate channel permissions)."""
    for channel in MONITORED_CHANNELS:
        now = dt.utcnow()
        shift_starts = [s['utc_start'] for s in SHIFTS]
        # Shift prepares to end between (start-1):50 and (start-1):59
        if now.hour in [start - 1 for start in shift_starts] and 50 <= now.minute <= 59:
            announce_shift_preparing(bot, channel)
        # Shift ends between (start):10 and (start):19
        elif now.hour in shift_starts and 10 <= now.minute <= 19:
            announce_shift_complete(bot, channel)


@module.interval(60)
def refresh_monitored_channels(bot):
    """Ensures the list of monitored channels is constantly up to date, especially following a reboot."""
    for channel in bot.channels:
        if bot.db.get_channel_value(channel, 'oncall'):
            if channel not in MONITORED_CHANNELS:
                MONITORED_CHANNELS.append(channel)
                debug(bot, 'refresh_monitored_channels: Adding {channel} to MONITORED_CHANNELS'.format(channel=channel))
        else:
            try:
                MONITORED_CHANNELS.remove(channel)
                debug(bot,
                      'refresh_monitored_channels: Removing {channel} from MONITORED_CHANNELS'.format(channel=channel))
            except ValueError:
                pass


@module.rule('.*')
@module.priority('high')
def refer_to_topic(bot, trigger):
    """If any 'monitored channels' are mentioned in their own channel, refer the user to shift-lead or on-call user."""
    if trigger.sender in MONITORED_CHANNELS and str(trigger.sender)[1:] in str(trigger):
        bot.say('Please reach out to the shift lead or on-call SRE')
        say_shift_leads(bot, trigger)


@module.rule('.*')
@module.rate(channel=600)
def monitor_weekend(bot, trigger):
    """Reminds users that channels are un-monitored on weekends. Will not trigger more than once every 10 minutes."""
    if trigger.sender in MONITORED_CHANNELS and dt.utcnow().weekday() > 4:
        leads = get_shift_leads(bot, trigger.sender)
        bot.reply('This channel is unmonitored on weekends. See {url} for Engineer Escalations'.format(
            oncall=leads[ONCALL['name']], url=ESCALATION_URL))


@module.rule(SNOW_TICKET_REGEX)
def snow_ticket(bot, trigger):
    """Provides the SNOW ticket URL."""
    bot.say(SNOW_SEARCH + trigger.groupdict()['ticket'])
