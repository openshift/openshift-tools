#!/bin/bash -e
#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 



echo -n "Running oso-centos7-bastion... "

# TODO: Remove privileged, net=host and OO_PAUSE_ON_START
sudo docker run --rm=true -it --name oso-centos7-bastion    \
            --user 1000                                   \
            --privileged                                  \
            --net=host                                    \
            --env OO_PAUSE_ON_START=true                  \
            -v /var/lib/docker/volumes/shared:/shared:rw  \
            oso-centos7-bastion $@

echo "Done."
