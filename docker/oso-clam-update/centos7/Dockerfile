# /usr/local/bin/start.sh will start the service

FROM openshifttools/oso-centos7-ops-base:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

# Install clam-update
RUN yum-install-check.sh -y clamav-update \
                            clamav-unofficial-sigs \
                            python2-boto3 \
                            python2-botocore \
                            openshift-tools-scripts-monitoring \
                            openshift-tools-scripts-clam-update \
                            && \
    yum clean all

# Add playbooks folder
ADD playbooks/ /var/lib/clamav/

RUN chown -R clamupdate:clamupdate /etc/clamav-unofficial-sigs && \
    chown -R clamupdate:clamupdate /usr/local/sbin /var/log/clamav-unofficial-sigs /var/lib/clamav-unofficial-sigs && \
    chown -R clamupdate:clamupdate /var/lib/clamav/ && \
    chown -R clamupdate:clamupdate /etc/openshift_tools && \
    chown clamupdate:clamupdate /usr/bin/clamav-unofficial-sigs.sh && \
    chown clamupdate:clamupdate /usr/bin/freshclam

RUN chsh -s /bin/bash clamupdate

RUN sed -i -e 's/reload_dbs="yes"/reload_dbs="no"/' /etc/clamav-unofficial-sigs/clamav-unofficial-sigs.conf && \
    sed -i -e 's/--max-time "$curl_max_time" //' /usr/bin/clamav-unofficial-sigs.sh && \
    sed -i -e 's/\$HOME\/.ansible\/tmp/\/var\/lib\/clamav\/.ansible\/tmp/' /etc/ansible/ansible.cfg && \
    sed -i -e 's/--connect-timeout "$curl_connect_timeout"//' /usr/bin/clamav-unofficial-sigs.sh

RUN rm -f /etc/cron.d/clamav-update /etc/cron.d/clamav-unofficial-sigs

# Make symlinks to /secret custom signature databases and config
RUN ln -sf /secrets/openshift_config.cfg /var/lib/clamav/openshift_config.cfg && \
    ln -sf /secrets/openshift_known_vulnerabilities.ldb /var/lib/clamav/openshift_known_vulnerabilities.ldb && \
    ln -sf /secrets/openshift_signatures.db /var/lib/clamav/openshift_signatures.db && \
    ln -sf /secrets/zagg-config-values.yaml /etc/openshift_tools/metric_sender.yaml && \
    ln -sf /secrets/openshift_signatures.hdb /var/lib/clamav/openshift_signatures.hdb && \
    ln -sf /secrets/openshift_signatures.ign2 /var/lib/clamav/openshift_signatures.ign2 && \
    ln -sf /secrets/openshift_signatures.ldb /var/lib/clamav/openshift_signatures.ldb && \
    ln -sf /secrets/openshift_whitelist.sfp /var/lib/clamav/openshift_whitelist.sfp
# Add necessary permissions to add arbitrary user
RUN chmod -R g+rwX /etc/passwd /etc/group

# run as clamupdate user
USER 999

ENV ANSIBLE_LOCAL_TEMP /var/lib/clamav/.ansible/tmp

# Start clam-update processes
ADD ops-run-in-loop start.sh /usr/local/bin/
ADD clamav-unofficial-sigs.conf /etc/clamav-unofficial-sigs/
CMD /usr/local/bin/start.sh
