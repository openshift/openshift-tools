# OpenShift SRE IRC Helper Function

## On-Call and Shift Lead Rotation

**IMPORTANT** https://cloud.google.com/storage/docs/authentication#service_accounts

    A Google Cloud service account JSON file is required to be able to access
    Google Sheet documents.

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

  > This channel is unmonitored on weekends. If you have a sev 1, submit a SNOW ticket to page the  on-call SRE ({oncall}). Submit your SNOW ticket at {url}

## SNOW Ticket parsing

Any SNOW tickets detected in a message will reply with an automatic link to the SNOW ticket

    https://redhat.service-now.com/surl.do?n=<SNOW_ticket>
