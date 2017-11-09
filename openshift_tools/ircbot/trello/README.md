# Trello Card API tools

A simple CLI and IRC bot to create, get and update Trello cards.

## Running CLI script

1. Edit `CREDENTIALS` file with environment variables for Trello key and oauth token
1. Source credentials file

        source CREDENTIALS
1. Run script

### Usage

See `./trello.py --help`

### Development Environment

See [Trello API documentation](https://trello.readme.io/reference).

## Running as IRC bot

IRC bot is based on the python [Sopel library](https://sopel.chat/). Decorated methods are triggered via a socket that Sopel keeps open. Sopel assumes config in `~/.sopel/default.cfg`.

IRC nicks are mapped to trello usernames using environment variables. Format is:

    IRCNICK_<ircnick>=<trello_username>

### IRC Bot dev environment

. Install sopel

        pip install sopel
. Create a ~/.sopel.default.cfg file. See `sopel.cfg.example`
. Source credentials file. See example `CREDENTIALS`

        . CREDENTIALS
. Run sopel irc bot in foreground

        sopel
. Join IRC channel and test
. Restart sopel server to reload changes to config or modules, e.g. trello.py

