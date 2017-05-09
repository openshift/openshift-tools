function buildAnsibleContainer {

    dockerTag=oso-${baseOS}-ansible:${ansibleVersion}
    bashScript=./oso-${baseOS}-ansible-playbook-${ansibleVersion}

    docker build --tag ${dockerTag} - << EndOfDockerfile
FROM ${baseOSfrom}

RUN yum -y update \
 && yum -y install ${ansibleRPM} \
 && yum clean all
EndOfDockerfile

    cat > ${bashScript} << EndOfBashScript
#!/bin/bash
#set -vx

sudo docker run --rm -it --privileged \\
  -v /etc/ansible:/etc/ansible:ro,rslave \\
  -v /usr/share/ansible/inventory/multi_inventory.py:/usr/share/ansible/inventory/multi_inventory.py:ro,rslave \\
  -v /:/host:ro,rslave \\
  -v /dev/shm/.ansible:/dev/shm/.ansible:ro,rslave \\
  -v \$SSH_AUTH_SOCK:/tmp/sshauth.sock \\
  -e SSH_AUTH_SOCK=/tmp/sshauth.sock \\
  -w /host/\`pwd\` \\
  ${dockerTag} \\
  /usr/bin/ansible-playbook \$@
EndOfBashScript

    chmod 755 ${bashScript}
}
