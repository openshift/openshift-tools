FROM registry.centos.org/centos/centos:7
MAINTAINER      Federico Simoncelli <fsimonce@redhat.com>

RUN yum update -y && \
    yum install -y golang openscap-scanner git && \
    yum clean all


COPY .  /go/src/github.com/openshift/image-inspector

RUN GOBIN=/usr/bin \
    GOPATH=/go \
    CGO_ENABLED=0 \
    go install -tags 'containers_image_openpgp exclude_graphdriver_devicemapper exclude_graphdriver_btrfs' \
    -a -installsuffix cgo \
    /go/src/github.com/openshift/image-inspector/cmd/image-inspector.go && \
    mkdir -p /var/lib/image-inspector

EXPOSE 8080

WORKDIR /var/lib/image-inspector

ENTRYPOINT ["/usr/bin/image-inspector"]
