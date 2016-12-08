#!/bin/bash
#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 


# mwoodson note 1-7-16:
# pcp recommends mounting /run in their Dockerfile
#  /run conflicts with cron which also runs in this container.
# I am leaving /run out for now.  the guys in #pcp said that they mounted /run
#  to shared the pcp socket that is created in /run. We are not using this,
#  as far as I know.
#  This problem goes away with systemd being run in the containers and not using
#   cron but using systemd timers
#           -v /run:/run                                     \

CONFIG_SOURCE=$(readlink -f ./container_setup)
sudo docker run --rm=true -it --name oso-rhel7-host-monitoring \
           --privileged                                     \
           --pid=host                                       \
           --net=host                                       \
           --ipc=host                                       \
           -v /etc/localtime:/etc/localtime:ro              \
           -v /sys:/sys:ro                                  \
           -v /sys/fs/selinux                               \
           -v /var/lib/docker:/var/lib/docker:ro            \
           -v /var/lib/docker/volumes/shared:/shared:rw     \
           -v /var/run/docker.sock:/var/run/docker.sock     \
           -v ${CONFIG_SOURCE}:/container_setup:ro \
           --memory 512m \
           oso-rhel7-host-monitoring $@
