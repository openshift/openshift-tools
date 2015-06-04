#!/bin/sh

curl https://openshift.zendesk.com/api/v2/tickets/${1}.json \
	  -H "Content-Type: application/json" -X PUT \
	    -d '{"ticket": {"status": "open", "group_id": 20824774, "comment": {"public": false, "body": "Ops de-escalation"}}}' \
	    -u $USERNAME/token:$TOKEN

echo ''


