#!/bin/bash

# Disable it for the current boot
echo off > /sys/devices/system/cpu/smt/control

# Disable it in grub as well
grubby --update-kernel=DEFAULT --args="nosmt"
