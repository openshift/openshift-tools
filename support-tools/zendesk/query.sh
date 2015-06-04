#!/bin/sh
curl "https://openshift.zendesk.com/api/v2/search.json" \
  -G --data-urlencode "query=type:ticket status:pending" \
  -u $USERNAME:$PASSWD

echo ''
