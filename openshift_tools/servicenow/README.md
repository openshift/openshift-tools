# Service Now Ticket CLI


## Running script

1. Edit `CREDENTIALS` file with environment variables for Service Now URL, username, password
1. Source credentials file

        source CREDENTIALS
1. Run script

        ./snow --help

## Usage

See `./snow --help`

As [noted in the ticketutil library](http://ticketutil.readthedocs.io/en/latest/ServiceNow.html), Service Now custom fields vary accross implmementations. Use the KEY=VALUE syntax to create or edit custom values. The field keys can be discovered by using `./snow.py get <ticketid>`.


## Logging

By default logging is set to 'INFO' level to STDOUT. Set env var 'TICKETUTIL_LOG_LEVEL'
to update log level: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'. See [ticketutil source](https://github.com/dmranck/ticketutil/blob/master/ticketutil/ticket.py#L14) for implementation.

## Development Environment

Service Now will host a development instance for you. See https://developer.servicenow.com/app.do#!/home

1. Install pip module. NOTE: you may need dependency RPM `krb5-devel`

        pip install --user ticketutil

