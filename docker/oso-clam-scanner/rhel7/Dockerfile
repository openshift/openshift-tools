# /usr/local/bin/start.sh will start the service

FROM oso-rhel7-ops-base:latest

# Pause indefinitely if asked to do so.
ARG OO_PAUSE_ON_BUILD
RUN test "$OO_PAUSE_ON_BUILD" = "true" && while sleep 10; do true; done || :

# Add root folder
ADD root/ /root/

# Make mount point for host filesystem
RUN mkdir -p /host

# Local install of python2-clamd, which is a prerequisite for scanpod-inmem
RUN yum install -y /root/python2-clamd-1.0.2-4.el7.noarch.rpm

# Install golang and the in-memory scanner
RUN yum install -y golang \
                   git \
		   python-requests \
                   openshift-tools-scripts-scanpod && \
    yum clean all

ADD . /go/src/github.com/openshift/clam-scanner

ENV GOBIN=/bin \
    GOPATH=/go

RUN go get github.com/golang/glog github.com/spf13/cobra github.com/spf13/pflag && \
    mkdir -p /go/src/golang.org/x/net && \
    cd /go/src/golang.org/x && \
    git clone https://github.com/golang/net.git --depth 1 && \
    cd  /go/src/github.com/openshift/clam-scanner && \
    go install && \
    cd && \
    rm -rf /go && \
    mkdir -p /run/clamd.scan /tmp/scan-data

# run as root user
USER 0

# Start processes
ADD ops-run-in-loop start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
