#!/bin/bash

#   Copyright 2016 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# Meant to be sourced by login shells
# Checks to see if the user logging in has credentials for all AWS accounts
# mentioned in /etc/openshift_tools/aws_accounts.txt and prompts them to create
# any that are missing. Also checks to make sure that credentials are securely
# stored and have not expired.

# Note: because we source this in the login shell, it needs to be compatible with bash and zsh.
# There are several places where -n "$ZSH_NAME" is tested to see if we're running zsh, and then
# the zsh version of the syntax is used instead of the bash version.

# only bash v4+ and zsh are supported. do nothing for other shells
if [ -n "$BASH_VERSION" -a "$BASH_VERSINFO" -gt 3 -o "$ZSH_NAME" ]; then

function _check_creds()
{
    local -A accounts
    local account_count creds_actual name num line regex now
    local credfile=~/.aws/credentials
    local expfile=~/.aws/credentials_expiration
    local minute=60
    local hour=$((minute * 60))
    local day=$((hour * 24))
    local week=$((day * 7))

    if ! private_encfs_mounted; then
        echo "~/.private not mounted. Skipping AWS credential check"
        return
    fi

    # if ~/.private/.aws doesn't exist, create it
    [ -d ~/.private/.aws ] || mkdir ~/.private/.aws
    # if ~/.private/.aws/credentials doesn't exist, create it
    if  [ ! -f ~/.private/.aws/credentials ]; then
      touch ~/.private/.aws/credentials
      chmod 600 ~/.private/.aws/credentials
    fi
    # if ~/.aws doesn't exist, create it as a symlink to ~/.private/.aws
    [ -d ~/.aws ] || ln -s ~/.private/.aws ~/.aws
    # if ~/.aws is a directory and ~/.aws/credentials doesn't exist, create it as a symlink to ~/.private/.aws/credentials
    [ -d ~/.aws -a ! -h ~/.aws -a ! -f .aws/credentials ] && ln -s ~/.private/.aws/credentials ~/.aws/credentials
    creds_actual=$(readlink -f ~/.aws/credentials)
    if [ "$creds_actual" != ~/.private/.aws/credentials ]; then
        echo "WARNING WARNING WARNING WARNING WARNING WARNING WARNING"
        echo ~/.aws/credentials must be stored in the encrypted directory ~/.private
        echo "WARNING WARNING WARNING WARNING WARNING WARNING WARNING"
    fi

    [ -f "$expfile" ] && read -r line < "$expfile"
    line=$((line+0))
    if [ -z "$ZSH_NAME" ]; then
        #    like 'date +%s' without a fork/exec
        now="$(printf '%(%s)T' -1)"
    else
        # zsh's printf doesn't have time formatters so we're forced to fork/exec date
        now="$(date +%s)"
    fi
    if [ $((now + week)) -gt "$line" ]; then
        if [ "$now" -gt "$line" ]; then
            echo "AWS credentials have expired. Run the following command to refresh them:"
        else
            echo "AWS credentials will expire in $(((line-now)/day)) day(s)," \
                "$(((line-now)%day/hour)) hour(s). Run the following command to refresh them:"
        fi
        echo "aws_api_key_manager --all"

        return 0
    fi

    while IFS=: read -r name num; do
        accounts["$name"]="$num"
    done < /etc/openshift_tools/aws_accounts.txt
    # save the count to tell later if we already had any
    account_count="${#accounts[@]}"
    if [ -r "$credfile" ]; then
        while read -r line; do
            regex='^\[[a-zA-Z0-9_-]*\]$'
            if [[ "$line" =~ $regex ]]; then
                # strip off leading and trailing [ and ]
                line="${line#\[}"
                line="${line%\]}"
                if [ -n "${accounts["$line"]+is_set}" ]; then
                    if [ -n "$ZSH_NAME" ]; then
                        # zsh syntax for unset requires quotes on associative array keys, which would break bash
                        unset 'accounts["$line"]'
                    else
                        unset accounts["$line"]
                    fi
                elif [ "$line" != "default" ]; then
                    echo "AWS Credentials exist in $credfile for unrecognized (possibly stale?) account '$line'"
                fi
            fi
        done < "$credfile"
    fi
    if [ "$account_count" -eq "${#accounts[@]}" ]; then
        echo "AWS Credentials missing for all accounts. Add them with the following command:"
        echo "aws_api_key_manager --all"
    elif [ "${#accounts[@]}" -gt 0 ]; then
        echo "AWS Credentials missing for one or more accounts. Add them with the following command:"
        echo -n "aws_api_key_manager"
        if [ -n "$ZSH_NAME" ]; then
            # in zsh associative array keys syntax is (@k) instead of !
            for name in "${(@k)accounts[@]}"; do
                echo -n " -p '$name'"
            done
        else
            for name in "${!accounts[@]}"; do
                echo -n " -p '$name'"
            done
        fi
        echo
    fi
}

# Only bother to check aws credentials for non-root users with UID<1000 who are members of libra_ops
# UID<1000 because robot members of libra_ops, like opsmedic or autokeys have UID>=1000.
if [ $UID -lt 1000 -a $UID -ne 0 ] && id -nG | grep -qw libra_ops; then
    # Check if we're in a login shell and only run the automounter if we are
    if [ -n "$ZSH_NAME" ]; then
        # this works on linux, but isn't portable to other systems.
        # unfortunately no simple means of discovering whether this is a login
        # shell seems to exist from a sourced shell snippet in zsh :-(
        grep -q ^-zsh\\\> /proc/$$/cmdline && _check_creds
    else
      shopt -q login_shell && _check_creds
      unset -f _check_creds
    fi
fi

fi
