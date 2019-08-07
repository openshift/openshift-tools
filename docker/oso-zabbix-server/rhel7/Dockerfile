# Example docker run command
# docker run -p 10050:10050 -p 10051:10051 oso-rhel7-zabbix-server
# /usr/local/bin/start.sh will then start zabbix
# Default login:password to Zabbix is Admin:zabbix

FROM oso-rhel7-ops-base:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

EXPOSE 10050 10051

ADD zabbix.repo /etc/yum.repos.d/
ADD pdagent.repo /etc/yum.repos.d/
ADD ops-rpm.repo /etc/yum.repos.d/

# Install zabbix (and supporting tools) from zabbix repo

# By default docker recommends to install packages with tsflags=nodocs for space saving
# but in this case, we need it for this one package, because the DB schema is coming from the docs
RUN yum-install-check.sh -y --setopt=tsflags='' zabbix-server-mysql && \
    yum clean all
RUN yum-install-check.sh -y zabbix-agent zabbix-sender crontabs \
    mariadb openssh-clients openshift-tools-scripts-monitoring-zabbix-heal \
    pdagent pdagent-integrations && \
    yum -y update && \
    yum clean all

# Lay down zabbix conf
ADD zabbix/conf/zabbix_server.conf /etc/zabbix/
ADD zabbix/conf/zabbix_agentd.conf /etc/zabbix/
ADD zabbix/conf/zabbix_agent.conf /etc/zabbix/

# DB creation
ADD zabbix/db_create/createdb.sh /root/zabbix/

# DB paritioning procedure creation
ADD zabbix/db_create/create_db_partitioning_procedures.sh /root/zabbix/

# Add the zabbix partitioning script and partitioning monitoring script
ADD zabbix/db_create/zabbix_partition_maintenance.sh /usr/local/bin/
ADD zabbix/db_create/zabbix_partition_monitoring.sh /usr/local/bin/

# Add crontab for root
# Re-enable once we figure out how to run cron inside of openshift.
#ADD cronroot /var/spool/cron/root

# Add ansible stuff
ADD root /root

RUN mkdir -p /etc/openshift_tools

# Add zabbix alert script
ADD smtp_ses.py /usr/lib/zabbix/alertscripts/
ADD zbx2slack.py /usr/lib/zabbix/alertscripts/
RUN ln -s /usr/share/pdagent-integrations/bin/pd-zabbix /usr/lib/zabbix/alertscripts/

# Start mysqld, zabbix, and apache
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh

# Make the container work more consistently in and out of openshift
# BE CAREFUL!!! If you change these, you may bloat the image! Use 'docker history' to see the size!
RUN mkdir -p /run/zabbix /var/run/pdagent
RUN chmod -R g+rwX /etc/passwd /etc/zabbix /etc/openshift_tools /var/log /run /var/lib/pdagent /var/run/pdagent && \
    chgrp -R root /var/log /run /var/lib/pdagent
