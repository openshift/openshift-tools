# Example docker run command
# docker run -p 10050:10050 -p 10050:10050 -p 80:80 -p 443:443 oso-rhel7-zaio
# /root/start.sh will then start the mysqldb, zabbix, and httpd services.
# Default login:password to Zabbix is Admin:zabbix

FROM oso-rhel7-ops-base:latest

RUN echo "root:redhat" | chpasswd

RUN yum clean metadata && \
    yum install -y iproute iputils pylint python-pip \
        python-requests python-django \
        openshift-tools-web-zagg \
        python-openshift-tools-web \
        python-openshift-tools-monitoring \
        tree python-django-bash-completion httpd mod_wsgi && \
    yum clean all

RUN pip install djangorestframework && \
    pip install markdown && \
    pip install django-filter

RUN mkdir /tmp/metrics && chown apache.apache /tmp/metrics

# Start apache
ADD start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
