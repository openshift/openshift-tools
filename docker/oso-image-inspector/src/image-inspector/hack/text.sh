#!/bin/bash

# see https://github.com/openshift/origin/blob/master/hack/text.sh

# This file contains helpful aliases for manipulating the output text to the terminal as
# well as functions for one-command augmented printing.

# ii::text::reset resets the terminal output to default if it is called in a TTY
function ii::text::reset() {
	if [ -t 1 ]; then
		tput sgr0
	fi
}

# ii::text::bold sets the terminal output to bold text if it is called in a TTY
function ii::text::bold() {
	if [ -t 1 ]; then
		tput bold
	fi
}

# ii::text::red sets the terminal output to red text if it is called in a TTY
function ii::text::red() {
	if [ -t 1 ]; then
		tput setaf 1
	fi
}

# ii::text::green sets the terminal output to green text if it is called in a TTY
function ii::text::green() {
	if [ -t 1 ]; then
		tput setaf 2
	fi
}

# ii::text::blue sets the terminal output to blue text if it is called in a TTY
function ii::text::blue() {
	if [ -t 1 ]; then
		tput setaf 4
	fi
}

# ii::text::yellow sets the terminal output to yellow text if it is called in a TTY
function ii::text::yellow() {
	if [ -t 1 ]; then
		tput setaf 11
	fi
}

# ii::text::clear_last_line clears the text from the last line of output to the
# terminal and leaves the cursor on that line to allow for overwriting that text
# if it is called in a TTY
function ii::text::clear_last_line() {
	if [ -t 1 ]; then 
		tput cuu 1
		tput el
	fi
}

# ii::text::print_bold prints all input in bold text
function ii::text::print_bold() {
	ii::text::bold
	echo "${*}"
	ii::text::reset
}

# ii::text::print_red prints all input in red text
function ii::text::print_red() {
	ii::text::red
	echo "${*}"
	ii::text::reset
}

# ii::text::print_red_bold prints all input in bold red text
function ii::text::print_red_bold() {
	ii::text::red
	ii::text::bold
	echo "${*}"
	ii::text::reset
}

# ii::text::print_green prints all input in green text
function ii::text::print_green() {
	ii::text::green
	echo "${*}"
	ii::text::reset
}

# ii::text::print_green_bold prints all input in bold green text
function ii::text::print_green_bold() {
	ii::text::green
	ii::text::bold
	echo "${*}"
	ii::text::reset
}

# ii::text::print_blue prints all input in blue text
function ii::text::print_blue() {
	ii::text::blue
	echo "${*}"
	ii::text::reset
}

# ii::text::print_blue_bold prints all input in bold blue text
function ii::text::print_blue_bold() {
	ii::text::blue
	ii::text::bold
	echo "${*}"
	ii::text::reset
}

# ii::text::print_yellow prints all input in yellow text
function ii::text::print_yellow() {
	ii::text::yellow
	echo "${*}"
	ii::text::reset
}

# ii::text::print_yellow_bold prints all input in bold yellow text
function ii::text::print_yellow_bold() {
	ii::text::yellow
	ii::text::bold
	echo "${*}"
	ii::text::reset
}
