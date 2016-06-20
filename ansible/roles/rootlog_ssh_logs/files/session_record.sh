# If the session is interactive and we haven't already started recording, start recording
if [[ "$-" =~ i ]] && [ -z "$SESSION_RECORD_FILE" ]; then
  who="${SUDO_USER:-$SSH_KEYNAME}"
  # if neither $SUDO_USER nor $SSH_KEYNAME was set, try to figure out the user with "who am i"
  if [ -z "$who" ]; then
    who="$(who am i)"
    who="${who%% *}"
    # if we still don't know, see if any ancestor process had SSH_KEYNAME or SUDO_USER in its env
    if [ -z "$who" -o "$who" == "root" ]; then
      pid=$$
      while [ -n "$pid" -a "$pid" != 0 ]; do
        who="$(strings /proc/$pid/environ | sed -n 's/^\(SSH_KEYNAME\|SUDO_USER\)=//p' | head -1)"
        [ -n "$who" -a "$who" != "root" ] && break
        unset who
        pid="$(echo $(ps -o ppid= -p "$pid" | head -1))"
      done
    fi
  fi
  if [ -n "$who" ]; then
    export SESSION_RECORD_FILE="/var/log/rootlog/sessions/$(date +'%Y-%m-%d-%H.%M.%S' )-$who-$RANDOM"
    exec script -q -f -t "$SESSION_RECORD_FILE" 2>"$SESSION_RECORD_FILE.timing"
  fi
  unset who pid
fi
