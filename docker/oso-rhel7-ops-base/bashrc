# .bashrc

# User specific aliases and functions

alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias vi=vim

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Set the prompt to the container id
# We explicitly do this so that it looks like a container even with:
#   --net=host
#   --net=container
# Both of these docker run options give confusing bash prompts inside the container.
CTR_ID=$(echo $container_uuid | awk '{ gsub(/-/,"",$1); print substr($1,1,13)}')
export PS1="[CTR][\u@$CTR_ID \W]\$ "
