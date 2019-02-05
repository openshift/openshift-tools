#!/bin/bash

IAM_PROFILE=$(curl 169.254.169.254/latest/meta-data/iam/info | jq -r '.InstanceProfileArn')
CLUSTERNAME=$(echo $IAM_PROFILE | awk -F/ '{split($2,a,"-iam_"); print a[1] }')
NODETYPE=$(echo $IAM_PROFILE | awk -F/ '{split($2,a,"-iam_"); print a[2] }')
INTERNAL_HOSTNAME=$(curl 169.254.169.254/latest/meta-data/local-hostname)

nohup /usr/bin/redhat-access-insights --register --display-name=$CLUSTERNAME-$NODETYPE-$INTERNAL_HOSTNAME --group=$CLUSTERNAME &
