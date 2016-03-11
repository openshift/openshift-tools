#!/bin/bash
#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 


sudo echo -e "\nTesting sudo works...\n"

sudo docker run -ti --rm --name oso-centos7-zagg-web \
  --link oso-centos7-zaio:oso-centos7-zaio \
  -e "ZAGG_SERVER_USER=admin" \
  -e "ZAGG_SERVER_PASSWORD=password" \
  -v /etc/localtime:/etc/localtime \
  -v /var/lib/docker/volumes/shared:/shared:rw \
  -p 8000:8000 \
  -p 8443:8443 \
  oso-centos7-zagg-web $1
