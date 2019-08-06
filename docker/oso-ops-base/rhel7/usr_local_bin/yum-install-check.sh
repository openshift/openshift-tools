#!/bin/bash

set -o errexit

yum install "$@"

for arg in "$@"; do
    case "$arg" in
        -*)
            ;;
        *)
            if ! yum list installed "$arg" &>/dev/null; then
                msg="${msg}${msg:+$'\n'}Error: Package not installed: $arg"
            fi
            ;;
    esac
done

if [ -n "$msg" ]; then
    echo
    echo "$msg"
    echo
    exit 1
fi
