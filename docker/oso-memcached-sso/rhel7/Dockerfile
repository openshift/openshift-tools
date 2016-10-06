#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 

# /usr/local/bin/start.sh will start the memcached service

FROM openshift/base-centos7 

# Install memcached
RUN yum -y install memcached && \
    yum clean all

# Expose port 11211
EXPOSE 11211

# Start memcached
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
