#     ___ ___ _  _ ___ ___    _ _____ ___ ___         
#    / __| __| \| | __| _ \  /_\_   _| __|   \        
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |       
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____ 
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |  
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|  
# 

# Example docker run command
# docker run -p 10050:10050 -p 10051:10051 -p 80:80 -p 443:443 oso-rhel7-zaio
# /usr/local/bin/start.sh will then start the mysqldb, zabbix, and httpd services.
# Default login:password to Zabbix is Admin:zabbix

FROM oso-centos7-ops-base:latest

# Pause indefinitely if asked to do so.
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while true ; do sleep 10 ; done || :

ADD zabbix.repo /etc/yum.repos.d/

# Install zabbix (and supporting tools) from zabbix repo
RUN yum install -y mod_ssl zabbix-server-mysql zabbix-sender zabbix-agent \
    zabbix-web-mysql mariadb mariadb-server openssh-clients openshift-tools-scripts-monitoring-zabbix-heal && \
    yum -y update && \
    yum clean all

ADD root/ /root/
# WORK AROUND FOR SQL SCRIPTS ARE MISSING
ADD zabbix/db_create/zdata /usr/share/doc/zabbix-server-mysql-2.4.5/create/

# Add mysql files
ADD mariadb-prepare-db-dir /usr/libexec/
ADD my.cnf /etc/

# Add zabbix mysql files
ADD zabbix/db_create/createdb.sh /root/
ADD zabbix/db_create/create_zabbix.sql /root/

# Lay down zabbix conf
ADD zabbix/conf/zabbix_server.conf /etc/zabbix/
ADD zabbix/conf/zabbix_agentd.conf /etc/zabbix/
ADD zabbix/conf/zabbix_agent.conf /etc/zabbix/

# Set the timezone in the php.ini file
RUN sed -r -ie 's/^;(date.timezone).*/\1 = America\/New_York/g' /etc/php.ini

# Zabbix web
ADD zabbix/conf/zabbix.conf.php /etc/zabbix/web/

# Rhel 7.2 update
ADD httpd.conf /etc/httpd/conf/
RUN sed -i -e 's/^\(LoadModule auth_digest_module modules\/mod_auth_digest.so\)$/#\1/g' /etc/httpd/conf.modules.d/00-base.conf

# Start mysqld, zabbix, and apache
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
