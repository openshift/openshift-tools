#!/bin/bash
set -vx

function buildAnsible {
    dockerTag=oso-ansible:${ansibleVersion}

    bashScript=./oso-ansible-playbook-${ansibleVersion}

    docker build --tag ${dockerTag} - << EndOfDockerfile
FROM fedora:25

RUN yum -y update \
 && yum -y install ${ansibleRPM} \
 && yum clean all
EndOfDockerfile

    cat > ${bashScript} << EndOfBashScript
#!/bin/bash
#set -vx

sudo docker run --rm -it --privileged \\
  -v /etc/ansible:/etc/ansible:ro \\
  -v /usr/share/ansible/inventory/multi_inventory.py:/usr/share/ansible/inventory/multi_inventory.py:ro \\
  -v /:/host:ro \\
  -v /dev/shm/.ansible:/dev/shm/.ansible:ro \\
  -v \$SSH_AUTH_SOCK:/tmp/sshauth.sock \\
  -e SSH_AUTH_SOCK=/tmp/sshauth.sock \\
  -w /host/\`pwd\` \\
  ${dockerTag} \\
  /usr/bin/ansible-playbook \$@
EndOfBashScript

    chmod 755 ${bashScript}
}

export ansibleRPM=https://kojipkgs.fedoraproject.org/packages/ansible/2.2.2.0/1.fc25/noarch/ansible-2.2.2.0-1.fc25.noarch.rpm
export ansibleVersion=2.2.2.0-1
buildAnsible

export ansibleRPM=https://kojipkgs.fedoraproject.org/packages/ansible/2.3.0.0/3.fc25/noarch/ansible-2.3.0.0-3.fc25.noarch.rpm
export ansibleVersion=2.3.0.0-3
buildAnsible
