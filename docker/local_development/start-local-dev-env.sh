#!/bin/bash -e

RED="$(echo -e '\033[1;31m')"
GREEN="$(echo -e '\033[1;32m')"
NORM="$(echo -e '\033[0m')"


# TODO:
# - add check for local web server on port 80/443
# - add check for host based pcp, that will mess with host-monitoring container failing with weird errors
cd $(dirname "$0")

OS_TEMPLATE="./zabbix_monitoring_cent7_local_dev.yaml"
OS_TEMPLATE_NAME="ops-cent7-zabbix-monitoring"
OPENSHIFT_TOOLS_REPO=$(readlink -f ./repo_root)

# Make sure 'oc' binary in path
OC=$(which oc)
if [ "$?" -ne "0" ]; then
	echo "Could not find 'oc' binary in path"
	exit 1
fi

OC_RUNNING=$(curl -s -o /dev/null -w %{http_code} -k https://localhost:8443/healthz || :)
if [ "${OC_RUNNING}" -eq "200" ]; then
	echo "It appears that OpenShift is already running."
	echo "Run stop-local-dev-env.sh script to clean up."
	exit
fi

echo "Opening ports on default zone for DNS and container traffic (non-permanent)"
sudo firewall-cmd --add-source 172.17.0.0/16
sudo firewall-cmd --add-port 8443/tcp
sudo firewall-cmd --add-port 53/udp
sudo firewall-cmd --add-port 8053/udp

sudo ${OC} cluster up
${OC} login localhost:8443 -u developer -p developer --insecure-skip-tls-verify
${OC} new-project monitoring

${OC} secrets new monitoring-secrets ./monitoring-secrets/*

# Create SSL certs if necessary
if [ ! -e "rootCA.pem" ] || [ ! -e "rootCA.key" ]; then
	echo "Creating root CA files..."
	NEW_ROOT_CA="true"
	openssl genrsa -out rootCA.key 2048
	openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 \
		-out rootCA.pem \
		-subj "/C=US/ST=North Carolina/L=Raleigh/O=Local Zabbix/CN=root"
fi

if [ "$NEW_ROOT_CA" == "true" ] || \
   [ ! -e "zabbix-web.key" ] || \
   [ ! -e "zabbix-web.crt" ]; then
	echo "Creating zabbix-web cert files..."
	openssl genrsa -out zabbix-web.key 2048
	openssl req -new -key zabbix-web.key -out zabbix-web.csr \
		-subj "/C=US/ST=North Carolina/L=Raleigh/O=Zabbix Web/CN=oso-cent7-zabbix-web"
	openssl x509 -req -in zabbix-web.csr -CA rootCA.pem -CAkey rootCA.key \
		-CAcreateserial -out zabbix-web.crt -days 500 -sha256
fi

if [ "$NEW_ROOT_CA" == "true" ] || \
   [ ! -e "zagg-web.key" ] || \
   [ ! -e "zagg-web.crt" ]; then
	echo "Creating zagg-web cert files..."
	openssl genrsa -out zagg-web.key 2048
	openssl req -new -key zagg-web.key -out zagg-web.csr \
		-subj "/C=US/ST=North Carolina/L=Raleigh/O=Zagg Web/CN=oso-cent7-zagg-web"
	openssl x509 -req -in zagg-web.csr -CA rootCA.pem -CAkey rootCA.key \
		-CAcreateserial -out zagg-web.crt -days 500 -sha256
fi

# Insert SSL certs into template
IFS=''
while read LINE; do
	case "$LINE" in
		*PLACE_ROOT_CA_HERE*) sed -e 's/^/        /' rootCA.pem
			;;
		*PLACE_ZABBIX_WEB_SSL_CERT_HERE*) sed -e 's/^/        /' zabbix-web.crt
			;;
		*PLACE_ZABBIX_WEB_SSL_KEY_HERE*) sed -e 's/^/        /' zabbix-web.key
			;;
		*PLACE_ZAGG_WEB_SSL_CERT_HERE*) sed -e 's/^/        /' zagg-web.crt
			;;
		*PLACE_ZAGG_WEB_SSL_KEY_HERE*) sed -e 's/^/        /' zagg-web.key
			;;
		*) echo "$LINE"
			;;
	esac
done < $OS_TEMPLATE > template_with_certs.yaml

${OC} create -f template_with_certs.yaml
${OC} process ${OS_TEMPLATE_NAME} | ${OC} create -f -

# These are not needed anymore, because DCs autodeploy, but I shall leave it in here in case we need to trigger
# it manually, in next iterations I would like to add these as an option
#echo "Deploying mysql pod"
#${OC} deploy --latest mysql --follow

#echo "Deploying zabbix-server pod"
#${OC} deploy --latest oso-cent7-zabbix-server --follow

#echo "Deploying zabbix-web pod"
#${OC} deploy --latest oso-cent7-zabbix-web --follow

GREP_RESULT=$(grep "oso-cent7-zabbix-web" /etc/hosts || :)
if [ "${GREP_RESULT}" == "" ]; then
        echo "Making /etc/hosts entry for zabbix-web"
	sudo bash -c "echo '127.0.0.1  oso-cent7-zabbix-web' >> /etc/hosts"
fi

GREP_RESULT=""
echo -n "Waiting for zabbix to be ready"
while [ "$GREP_RESULT" == "" ]; do
	sleep 1
	echo -n "."
	GREP_RESULT=$(curl -k https://oso-cent7-zabbix-web/zabbix/ 2>/dev/null | grep 'sign in as guest' || :)
done

echo " Done"
echo "Config zabbix"
PYTHONPATH=${OPENSHIFT_TOOLS_REPO}:${PYTHONPATH} ansible-playbook ../../ansible/playbooks/adhoc/zabbix_setup/oo-clean-zaio.yml -e g_server="https://oso-cent7-zabbix-web/zabbix/api_jsonrpc.php"
PYTHONPATH=${OPENSHIFT_TOOLS_REPO}:${PYTHONPATH} ansible-playbook ../../ansible/playbooks/adhoc/zabbix_setup/oo-config-zaio.yml -e g_server="https://oso-cent7-zabbix-web/zabbix/api_jsonrpc.php"

echo "Deploying zagg pod"
${OC} deploy --latest oso-cent7-zagg-web --follow

GREP_RESULT=$(grep "oso-cent7-zagg-web" /etc/hosts || :)
if [ "${GREP_RESULT}" == "" ]; then
        echo "Making /etc/hosts entry for zagg-web"
	sudo bash -c "echo '127.0.0.1  oso-cent7-zagg-web' >> /etc/hosts"
fi
echo "Give zagg container time to finish starting up"
sleep 10

echo "Starting host monitoring"
CONTAINER_SETUP_DIR=$(readlink -f ./container_setup)
sudo docker run --name oso-centos7-host-monitoring -d \
	--privileged \
	--pid=host \
	--net=host \
	--ipc=host \
	-v /etc/localtime:/etc/localtime:ro \
	-v /sys:/sys:ro \
	-v /sys/fs/selinux \
	-v /var/lib/docker:/var/lib/docker:ro \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-v ${CONTAINER_SETUP_DIR}:/container_setup:ro \
	-v /var/lib/docker/volumes/shared:/shared \
	--memory 512m \
        docker.io/openshifttools/oso-centos7-host-monitoring:latest

echo
echo
echo "Log into the OpenShift console at ${GREEN}https://localhost:8443/console/${NORM} (username: developer / password: developer)"
echo
echo "Log into zabbix at ${GREEN}https://oso-cent7-zabbix-web/zabbix/${NORM} (username: Admin / password: zabbix)"
echo
echo "Connect to host-monitoring with: ${GREEN}sudo docker exec -ti oso-centos7-host-monitoring bash${NORM}"
echo
