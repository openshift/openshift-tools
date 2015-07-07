FROM oso-rhel7-ops-base:latest

RUN yum clean metadata && \
    yum install -y python-pip pcp pcp-conf pcp-testsuite \
        python-requests \
        python-openshift-tools-web \
        python-openshift-tools-monitoring \
        openshift-tools-scripts-monitoring \
        pcp-manager pcp-webapi python-pcp && \
    yum clean all
