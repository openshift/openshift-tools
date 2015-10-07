#!/bin/bash -e

function print_usage() {
  echo
  echo "Usage: $(basename $0) [OPTION]... [COMMAND]"
  echo
  echo "  -n NAME     Name identifier for this command."
  echo "  -c          Command to run. This is mainly used when shell is embedded in the command."
  echo
  echo "Examples:"
  echo "  Everything after the options will be run as the command."
  echo "    $(basename $0) -n example.command /bin/cp /etc/issue /tmp/issue"
  echo
  echo "  Alternatively, -c can be used to embed shell code in the command:"
  echo "    $(basename $0) -n example.command -c 'for i in {1..100}; do echo $i; done'"
  echo
}

function die() {
  echo "$1"
  exit 10
}

# They probably want to see the help screen
if [ $# -eq 0 -o "$1" == "--help" ] ; then
  print_usage
  exit
fi

NAME=""
COMMAND=""

while getopts ":n:c:h" opt; do
  case $opt in
    n)
      NAME=$OPTARG
      ;;
    c)
      COMMAND=$OPTARG
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

# So that this script doesn't die if the passed in command returns a non-zero exit code
set +e
if [ ! -z "$COMMAND" ] ; then
  bash -c "$COMMAND"
  EXITCODE=$?
else
  # Joel approved, much more secure than eval, and has less quoting issues.
  # DO NOT CHANGE THIS TO EVAL!!!
  "$@"
  EXITCODE=$?
fi
set -e

# Create our dynamic item for this command
ops-zagg-client --discovery-key disc.ops.runner --macro-string '#OSO_COMMAND' --macro-names "$NAME"

# Send the data
ops-zagg-client -k "disc.ops.runner.command.exitcode[$NAME]" -o $EXITCODE
