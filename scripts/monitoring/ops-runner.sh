#!/bin/bash -e

function cleanup() {
  [ -e "$TEMP_FILE" ] && rm $TEMP_FILE
}

trap cleanup EXIT

function print_usage() {
  echo
  echo "Usage: $(basename $0) [OPTION]... [COMMAND]"
  echo
  echo "  -n NAME     Name identifier for this command."
  echo "  -c          Command to run. This is mainly used when shell is embedded in the command."
  echo "  -s          Sleep time, random. Insert a random sleep between 1 and X number of seconds."
  echo
  echo "Examples:"
  echo "  Everything after the options will be run as the command."
  echo "    $(basename $0) -n example.command /bin/cp /etc/issue /tmp/issue"
  echo
  echo "  Insert random sleep between 1 and 100 seconds of the previous example."
  echo "    $(basename $0) -s 100 -n example.command /bin/cp /etc/issue /tmp/issue"
  echo
  echo "  Alternatively, -c can be used to embed shell code in the command:"
  echo "    $(basename $0) -n example.command -c 'for i in {1..100}; do echo $i; done'"
  echo
}

function log() {
  # Mmm DD hh:mm:ss
  DATE=$(date +"%b %d %H:%M:%S")
  HOST=$(hostname)

  # Replace newlines with '~' so we can do a single-line log entry
  NO_NEWLINES=$(echo "$1" | tr '\n' '~')
  printf "%s %s %s: %s\n" "$DATE" "$HOST" "$NAME" "$NO_NEWLINES" >> /var/log/ops-runner.log
}

function die() {
  echo "$1" >&2
  exit 10
}

# They probably want to see the help screen
if [ $# -eq 0 -o "$1" == "--help" ] ; then
  print_usage
  exit
fi

NAME=""
COMMAND=""
SLEEP=""

while getopts ":n:c:s:h" opt; do
  case $opt in
    n)
      NAME=$OPTARG
      ;;
    c)
      COMMAND=$OPTARG
      ;;
    s)
      SLEEP=$OPTARG
      ;;
    h)
      print_usage
      exit
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 5
      ;;
  esac
done

# Shift out all of the parsed options, leaving just the supplied command
shift $(expr $OPTIND - 1)

# Make sure a name identifier was passed
test -z "$NAME" && die "ERROR: -n is a required option"

# Make sure a command was passed, one way or another
test $# -eq 0 -a -z "$COMMAND" && die "ERROR: No command given"

# Make sure only 1 command was passed, one way or another
test $# -gt 0 -a ! -z "$COMMAND" && die "ERROR: Too many commands given"

# If we need to sleep, let's random sleep
if [ ! -z "$SLEEP" ] ; then
   sleep $(( $RANDOM % $SLEEP  + 1 ))s
fi

TEMP_FILE=$(mktemp ops-runner-${NAME}-XXXXXXXXXX)
# So that this script doesn't die if the passed in command returns a non-zero exit code
set +e
if [ ! -z "$COMMAND" ] ; then
  bash -c "$COMMAND" | tee $TEMP_FILE
  EXITCODE=${PIPESTATUS[0]}
else
  # Joel approved, much more secure than eval, and has less quoting issues.
  # DO NOT CHANGE THIS TO EVAL!!!
  "$@" | tee $TEMP_FILE
  EXITCODE=${PIPESTATUS[0]}
fi
set -e

if [ "$EXITCODE" -ne "0" ] ; then
  log "`echo \"Exit code: ${EXITCODE}\" | cat $TEMP_FILE -`"
fi

echo "Exit code: ${EXITCODE}"

# Create our dynamic item for this command
ops-zagg-client --discovery-key disc.ops.runner --macro-string '#OSO_COMMAND' --macro-names "$NAME"

# Send the data
ops-zagg-client -k "disc.ops.runner.command.exitcode[$NAME]" -o $EXITCODE

# Exit with same code as what was just run
exit ${EXITCODE}
