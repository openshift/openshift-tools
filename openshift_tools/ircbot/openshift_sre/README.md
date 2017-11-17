# OpenShift SRE IRC Helper Function

## On-Call and Shift Lead Rotation

**IMPORTANT** 

    A Google Cloud service account JSON file is required to be able to access
    Google Sheet documents. Additionally, the "Drive API" and "Sheets API"
    must be enabled for the project.

* Creating a service account: https://cloud.google.com/storage/docs/authentication#service_accounts
* Enabling the APIs (see steps 2 & 3): https://pygsheets.readthedocs.io/en/latest/authorizing.html

***

Provides the following commands:

* `.track <google_sheet_url>`
  * Begins tracking on-call and shift lead rotations from a provided google spreadsheet
  * Becomes a [monitored](#channel-monitoring) channel
* `.untrack`
  * Stops tracking on-call and shift lead rotations for channel
  * Is no longer a [monitored](#channel-monitoring) channel
* `.shift`
  * Lists the current on-call and shift leads for this rotation period
* `.monitored-channels`
  * Sends PRIVMSG of all channels currently monitored for on-call and shift lead rotations
  * Will only respond to bot admins
* `.snow`
  * Responds with the SNOW OpenShift SRE Service Request Form
  * https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form

### Channel Monitoring

Monitored channels have the follow features:

* Approximately 10 minutes *before* a defined shift change, the following message will be displayed

  > {curr_shift} preparing to sign off, {next_shift} preparing to take over the environment  
  > {curr_nick}: What happened today? What does {next_nick} need to know about?  
  > Check SNOW ticket queue here {queue}

* Approximately 15 minutes *after* a defined shift change, the following message will be displayed

  > Shift change complete  
  > Shift Lead: {curr_nick}  
  > On-Call: {oncall_nick}  
  > Thanks {prev_shift}, enjoy your evening!

* The channel topic will be updated following a shift change with the following message

  > Current Shift Lead: {lead} - OnCall: {oncall} - Shift Change at: {time}UTC (Brisbane - {time}; Beijing - {time}; Brno - {time}; Raleigh - {time}

* If a monitored channel is mentioned within its own channel, the `.shift` command will be called
* If a monitored channel has *any* IRC traffic on the weekend, it will display the following message (**NOTE** This message is not displayed more than once every 10 minutes)

  > This channel is unmonitored on weekends. See https://mojo.redhat.com/docs/DOC-1123528 for Engineer Escalations.

## SNOW Ticket parsing

Any SNOW tickets detected in a message will reply with an automatic link to the SNOW ticket

    https://redhat.service-now.com/surl.do?n=<SNOW_ticket>
    
    
## SalesForce Case parsing

Any SalesForce cases detected in a message will reply with an automatic message and link to the SalesForce case

    <nick>: Please make sure that there is a corresponding SNOW ticket for this case.
    <nick>: A SNOW ticket can be opened from https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form
    https://gss.my.salesforce.com/apex/Case_View?sbstr=<sfdc_case>
    
## Karma

Specifying <nick>++ will increase a nick's karma, and <nick>-- will decrease a nick's karma.

    NOTE: Karma can only be increased or decreased every 10 seconds to prevent spamming

* `.karma`
  * Provides your own karma
* `.karma <nick>`
  * Provides karma of <nick>

## .all Announcements

* `.all <message>`
  * Will announce <message> to all nicks within .all list
* `.all-add <nick>`
  * Adds <nick> to .all list
  * Will only respond to bot admins
* `.all-delete <nick>`
  * Removes <nick> from .all list
  * Will only respond to bot admins
* `.all-deleteall [confirm]`
  * Removes *all* nicks from .all list
  * If only acts if `confirm` is added in the command
  * Will only respond to bot admins
* `.all-list`
  * Lists all nicks in .all list

    
# Testing

## Google Sheets on-call integration

```
.track
    Not currently tracking an SRE on-call rotation.
    
.track https://docs.google.com/spreadsheets/d/1tm6Sx5sJvsPXHAhxoPdSs2ODCHwBquKJzn-ObgTeVRw/edit#gid=1539275069
    I can't seem to access that spreadsheet (https://docs.google.com/spreadsheets/d/1tm6Sx5sJvsPXHAhxoPdSs2ODCHwBquKJzn-ObgTeVRw/edit#gid=1539275069). Are you sure that the URl is correct and that <service_account_email> has been invited to that doc?

<Add service account email>

.track https://docs.google.com/spreadsheets/d/1tm6Sx5sJvsPXHAhxoPdSs2ODCHwBquKJzn-ObgTeVRw/edit#gid=1539275069
    #wgordon is now tracking SRE on-call rotation: https://docs.google.com/spreadsheets/d/1tm6Sx5sJvsPXHAhxoPdSs2ODCHwBquKJzn-ObgTeVRw/edit#gid=1539275069

wgordon  <- Matches whatever channel name is being tracked
    Please reach out to the shift lead or on-call SRE
    ONCALL: ihorvath
    NASA: sten
    EMEA: marek
    APAC: zhiwliu

.shift
    <something similar to>
    	ONCALL: ihorvath
        NASA: sten
        EMEA: marek
        APAC: zhiwliu

.monitored-channels
    <privmsg>
        <channel>
        
.untrack
    <channel> is no longer tracking SRE on-call rotations.
    
.untrack
    <channel> is not currently tracking SRE on-call rotations.
    
.monitored-channels
    <privmsg>
        No monitored channels.

<Any message sent on a weekend to a tracked channel>
    This channel is unmonitored on weekends. See https://mojo.redhat.com/docs/DOC-1123528 for Engineer Escalations.
```

## .all Announcing

```
.all test
    I don't have any users to send to. Try having an admin use `.all-add <nick>` to add someone.
    
.all-add test-nick
    The .all list has been initialized, and test-nick has been added.
    
.all test
    test-nick: test
    
.all-list
    .all list users:
    test-nick
    
.all-delete test-nick
    test-nick has been removed from the .all list.
    
.all test
    I don't have any users to send to. Try having an admin use `.all-add <nick>` to add someone.

.all-deleteall
    There are no users to delete.
    
.all-add test-nick2
    test-nick2 has been added to the .all list.

.all-deleteall
    This is a destructive command that will remove 1 users from the .all list.
    <nick>: If you still want to do this, please run: .all-deleteall confirm
    
.all-deleteall confirm
    I've removed all users from the .all list.
    
.all-list
    There are no users in .all list.
```

## Karma

```
.karma
    wgordon does not have any karma.
    
wgordon++
    You can't change your own karma.

sre-bot++
    sre-bot now has 1 karma.
    
sre-bot-- better-bot++
    sre-bot now has 0 karma.
    better-bot now has 1 karma.

.karma better-bot
    better-bot has 1 karma.
```

## Misc functionality

```
.snow
    https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form
    
.admins
    <privmsg>
        Current bot owner: wgordon
        No configured admins
        New admins can be added by creating a PR against https://github.com/openshift/openshift-ansible-ops/tree/prod/playbooks/adhoc/ircbot

RITM0220268
    https://redhat.service-now.com/surl.do?n=RITM0220268
    
01974620
    <nick>: Please make sure that there is a corresponding SNOW ticket for this case.
    <nick>: A SNOW ticket can be opened from https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form
    https://gss.my.salesforce.com/apex/Case_View?sbstr=01974620
```
