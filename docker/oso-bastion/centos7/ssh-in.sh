#!/bin/bash

connect_str=$(echo -en 'CONNECT 127.0.0.1:%p HTTP/1.1\r\nHost: %h:8443\r\n\r\n')

ssh -vvvv localhost -p 2222 -a -l user \
    -o "ProxyCommand=bash -c 'exec openssl s_client -servername %h -connect %h:8443 -quiet 2>/dev/null < <(echo -n ${connect_str} ; cat -)'"
