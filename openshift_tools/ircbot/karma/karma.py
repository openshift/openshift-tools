# coding=utf8
"""
karma.py

Original work Copyright 2014 Max Gurela
Modified work Copyright 2015 Red Hat

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import rate, rule, commands, require_privilege, OP # pylint: disable=import-error
from sopel.tools import Identifier # pylint: disable=import-error


@rate(10)
@rule(r'^([\S]+?)\+\+$')
# @commands('inc')
def promote_karma(bot, trigger):
    """
    Update karma status for specify IRC user if get '++' message.
    """
    if (trigger.is_privmsg):
        return bot.say('People like it when you tell them good things.')
    if (bot.db.get_nick_id(Identifier(trigger.group(1))) ==
            bot.db.get_nick_id(Identifier(trigger.nick))):
        return bot.say('You may not give yourself karma!')
    current_karma = bot.db.get_nick_value(trigger.group(1), 'karma')
    if not current_karma:
        current_karma = 0
    else:
        current_karma = int(current_karma)
    current_karma += 1

    bot.db.set_nick_value(trigger.group(1), 'karma', current_karma)
    bot.say(trigger.group(1) + ' == ' + str(current_karma))


@rate(10)
@rule(r'^([\S]+?)\-\-$')
# @commands('dec')
def demote_karma(bot, trigger):
    """
    Update karma status for specify IRC user if get '--' message.
    """
    if (trigger.is_privmsg):
        return bot.say('Say it to their face!')
    if (bot.db.get_nick_id(Identifier(trigger.group(1))) ==
            bot.db.get_nick_id(Identifier(trigger.nick))):
        return bot.say('You may not reduce your own karma!')
    current_karma = bot.db.get_nick_value(trigger.group(1), 'karma')
    if not current_karma:
        current_karma = 0
    else:
        current_karma = int(current_karma)
    current_karma -= 1

    bot.db.set_nick_value(trigger.group(1), 'karma', current_karma)
    bot.say(trigger.group(1) + ' == ' + str(current_karma))


@rate(10)
@rule(r'^([\S]+?)\=\=$')
def show_karma(bot, trigger):
    """
    Update karma status for specify IRC user if get '--' message.
    """
    current_karma = bot.db.get_nick_value(trigger.group(1), 'karma')
    if not current_karma:
        current_karma = 0
    else:
        current_karma = int(current_karma)

    bot.say(trigger.group(1) + ' == ' + str(current_karma))


@commands('karma')
# @example('.karma nick')
def karma(bot, trigger):
    """
    Command to show the karma status for specify IRC user.
    """
    nick = trigger.nick
    if trigger.group(2):
        nick = trigger.group(2).strip().split()[0]

    mykarma = bot.db.get_nick_value(nick, 'karma')
    if not mykarma:
        mykarma = '0'
    bot.say("%s == %s" % (nick, mykarma))


@require_privilege(OP)
@commands('setkarma')
# @example('.setkarma nick 99')
def set_karma(bot, trigger):
    """
    Set karma status for specific IRC user.
    """

    if trigger.group(2):
        nick = trigger.group(2).strip().split()[0]
        value = int(trigger.group(2).strip().split()[1])

    bot.db.set_nick_value(nick, 'karma', value)
    bot.say("%s == %s" % (nick, value))


@rate(10)
@commands('karmatop')
# @example('.karmatop 3')
def top_karma(bot, trigger):
    """
    Show karma status for the top n number of IRC users.
    """
    try:
        top_limit = int(trigger.group(2).strip())
    except (ValueError, AttributeError):
        top_limit = 5

    query = "SELECT DISTINCT slug, value FROM nick_values NATURAL JOIN nicknames \
        WHERE key = 'karma' ORDER BY value DESC LIMIT ?"
    karmalist = bot.db.execute(query, str(top_limit)).fetchall()
    for user in karmalist:
        bot.say("%s == %s" % (user[0], user[1]))
