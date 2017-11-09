# IRC bot

[Sopel IRC](https://sopel.chat/) modules


## Running

See [Sopel library](https://sopel.chat/). Decorated methods are triggered via a socket that Sopel keeps open. Sopel assumes config in `~/.sopel/default.cfg`.

### IRC Bot dev environment

. Install sopel

        pip install -r requirements
. Create a ~/.sopel.default.cfg file. See `sopel.cfg.example`
. Run sopel irc bot in foreground

        sopel
. Join IRC test channel for testing
. Restart sopel server to reload changes to config or modules, e.g. trello/trello.py

