# Example docker run command
# docker run -p 10050:10050 -p 10051:10051 oso-rhel7-zabbix-server
# /usr/local/bin/start.sh will then start zabbix
# Default login:password to Zabbix is Admin:zabbix

FROM oso-rhel7-ops-base:latest

EXPOSE 10050 10051

# Lay down the zabbix repository
RUN yum clean metadata && \
    yum install -y openshift-ops-yum-zabbix && \
    yum clean all

# Install zabbix from zabbix repo
RUN yum install -y zabbix-server-mysql zabbix-agent zabbix-sender crontabs \
    mariadb openssh-clients && \
    yum -y update && \
    yum clean all


# Lay down zabbix conf
ADD zabbix/conf/zabbix_server.conf /etc/zabbix/
ADD zabbix/conf/zabbix_agentd.conf /etc/zabbix/
ADD zabbix/conf/zabbix_agent.conf /etc/zabbix/

# WORK AROUND FOR SQL SCRIPTS ARE MISSING
ADD zabbix/db_create/zdata /usr/share/doc/zabbix-server-mysql-2.4.5/create/

# DB creation
ADD zabbix/db_create/createdb.sh /root/zabbix/
#ADD zabbix/db_create/create_zabbix.sql /root/zabbix/

# Add crontab for root
# Re-enable once we figure out how to run cron inside of openshift.
#ADD cronroot /var/spool/cron/root

# Add ansible stuff
ADD root /root

RUN mkdir /etc/openshift_tools

# Add zabbix alert script
ADD smtp_ses.py /usr/lib/zabbix/alertscripts/

# Start mysqld, zabbix, and apache
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh

# Make the container work more consistently in and out of openshift
# BE CAREFUL!!! If you change these, you may bloat the image! Use 'docker history' to see the size!
RUN chmod -R g+rwX /etc/passwd /etc/zabbix /etc/openshift_tools /var/log /run && \
    chgrp -R root /var/log /run
