#!/bin/bash

_ossh_helper_remote_completion()
{
    local cur
    cur=${COMP_WORDS[COMP_CWORD]}

    COMPREPLY=( $( compgen -W "`${OSSH_HELPER_CACHE}`" -- $cur ) )

    return 0
}

complete -F _ossh_helper_remote_completion -o filenames ossh
