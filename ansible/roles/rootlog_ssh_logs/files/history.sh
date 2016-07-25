# If the session is interactive and we haven't already set up history logging
if [[ "$-" =~ i ]] && ! [[ "$PROMPT_COMMAND" =~ history\ -a ]]; then
  shopt -s histappend
  # this PROMPT_COMMAND will have the shell flush the last command out to the
  # history file each time a prompt is displayed
  export PROMPT_COMMAND="history -a; history -c; history -r${PROMPT_COMMAND:+; }$PROMPT_COMMAND"
  export HISTCONTROL=""
  export HISTIGNORE=""
  # this will cause bash to log a timestamp for each history entry
  export HISTTIMEFORMAT="%F %T "
  # make a .bash_history file for each superuser. Use $SUDO_USER if set,
  # otherwise, use $SSH_KEYNAME
  who="${SUDO_USER:-$SSH_KEYNAME}"
  # if neither $SUDO_USER nor $SSH_KEYNAME was set, try to figure out the user with "who am i"
  if [ -z "$who" ]; then
    who="$(who am i)"
    who="${who%% *}"
    [ "$who" == "root" ] && unset who
    # if we still don't know, see if any ancestor process had SSH_KEYNAME or SUDO_USER in its env
    if [ -z "$who" ]; then
      pid=$$
      while [ -n "$pid" -a "$pid" != 0 ]; do
        who="$(strings /proc/$pid/environ | sed -n 's/^\(SSH_KEYNAME\|SUDO_USER\)=//p' | head -1)"
        [ -n "$who" -a "$who" != "root" ] && break
        unset who
        pid="$(echo $(ps -o ppid= -p "$pid" | head -1))"
      done
    fi
  fi
  # set to ~/.bash_history_$who (or ~/.bash_history if $who isn't set)
  export HISTFILE=~/.bash_history"${who:+_}$who"
  if [ ! -f "$HISTFILE" ]; then
    if [ -s ~/.bash_history ]; then
      cp -a ~/.bash_history "$HISTFILE"
    else
      # we can't just touch the new file. For some reason, bash wants a non-empty file
      # in order to use the $PROMPT_COMMAND trick that we use
      echo 'echo "new history file"' >> "$HISTFILE"
      chmod 0600 "$HISTFILE"
    fi
  fi
  unset who pid
fi
