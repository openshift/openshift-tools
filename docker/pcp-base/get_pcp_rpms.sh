#!/bin/bash

mkdir RPMS

for i in \
  pcp-3.10.5-1.fc22.x86_64.rpm \
  pcp-collector-3.10.5-1.fc22.x86_64.rpm \
  pcp-compat-3.10.5-1.fc22.x86_64.rpm \
  pcp-conf-3.10.5-1.fc22.x86_64.rpm \
  pcp-export-pcp2graphite-3.10.5-1.fc22.x86_64.rpm \
  pcp-gui-3.10.5-1.fc22.x86_64.rpm \
  pcp-import-collectl2pcp-3.10.5-1.fc22.x86_64.rpm \
  pcp-import-ganglia2pcp-3.10.5-1.fc22.x86_64.rpm \
  pcp-import-iostat2pcp-3.10.5-1.fc22.x86_64.rpm \
  pcp-import-mrtg2pcp-3.10.5-1.fc22.x86_64.rpm \
  pcp-import-sar2pcp-3.10.5-1.fc22.x86_64.rpm \
  pcp-libs-3.10.5-1.fc22.x86_64.rpm \
  pcp-libs-devel-3.10.5-1.fc22.x86_64.rpm \
  pcp-manager-3.10.5-1.fc22.x86_64.rpm \
  pcp-monitor-3.10.5-1.fc22.x86_64.rpm \
  pcp-system-tools-3.10.5-1.fc22.x86_64.rpm \
  pcp-testsuite-3.10.5-1.fc22.x86_64.rpm \
  pcp-webapi-3.10.5-1.fc22.x86_64.rpm \
  perl-PCP-LogImport-3.10.5-1.fc22.x86_64.rpm \
  perl-PCP-LogSummary-3.10.5-1.fc22.x86_64.rpm \
  perl-PCP-MMV-3.10.5-1.fc22.x86_64.rpm \
  perl-PCP-PMDA-3.10.5-1.fc22.x86_64.rpm \
  python-pcp-3.10.5-1.fc22.x86_64.rpm \
  python3-pcp-3.10.5-1.fc22.x86_64.rpm \
  pcp-debuginfo-3.10.5-1.fc22.x86_64.rpm;
do
  wget https://kojipkgs.fedoraproject.org//packages/pcp/3.10.5/1.fc22/x86_64/${i} -O /tmp/RPMS/${i}
done
