FROM openshift/origin:latest

# Reset the entrypoint
ENTRYPOINT ["/bin/sh", "-c"]

RUN yum install -y clamav-server clamav-scanner clamav-data --disablerepo=origin-local-release \
      && mkdir -p /image-data && chmod 0777 /image-data

# Copy the default clamav configuration. For custom configuration, create a VOLUME.
COPY clamd.conf /etc/clamd.d/local.conf

# Copy the scanner binary
COPY run-clam-scan/run-clam-scan /usr/bin/run-clam-scan

# Copy the image inspector binary
COPY image-inspector /usr/bin/image-inspector

CMD ["/usr/bin/run-clam-scan"]
