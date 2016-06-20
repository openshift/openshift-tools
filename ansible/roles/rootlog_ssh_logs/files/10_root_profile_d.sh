# for root (only), source any scriptlets from /root/.profile.d/
if [ "$UID" == "0" ]; then
  for i in /root/.profile.d/*.sh ; do
    if [ -r "$i" ]; then
      # check to see if this an interactive shell
      if [ "${-#*i}" != "$-" ]; then
        . "$i"
      else
        . "$i" >/dev/null 2>&1
      fi
    fi
  done
fi
