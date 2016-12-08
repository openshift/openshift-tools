#!/bin/bash
#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 



# Make sure base is pushed with the latest changes since we depend on it.
if ../../oso-ops-base/centos7/push.sh ; then
  # Push ourselves
  echo
  echo "Pushing oso-centos7-host-monitoring..."
  echo "Ensure you have successfully authenticated against docker with a 'docker login'"
  sudo docker push openshifttools/oso-centos7-host-monitoring
fi
