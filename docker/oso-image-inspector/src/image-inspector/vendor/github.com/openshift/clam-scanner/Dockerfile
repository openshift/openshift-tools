FROM openshift/origin-base

RUN yum install -y golang && yum clean all

ADD . /go/src/github.com/openshift/clam-scanner
RUN export GOBIN=/bin GOPATH=/go && \
    go get github.com/golang/glog github.com/spf13/cobra github.com/spf13/pflag && \
    cd  /go/src/github.com/openshift/clam-scanner && \
    go install && \
    rm -rf /go && \
    mkdir -p /run/clamd.scan /tmp/scan-data

ENTRYPOINT ["/bin/clam-scanner", "scan", "--path=/tmp/scan-data"]
