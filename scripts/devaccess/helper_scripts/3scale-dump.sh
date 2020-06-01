#!/bin/bash

THREESCALE_PROJECT="${1}"

COMPRESS_UTIL="${2,,}"

#CURRENT_DIR=$(dirname "$0")
CURRENT_DIR=$PWD

# Avoid fetching information about any pod that is not a 3scale one
THREEESCALE_PODS=("3scale-operator" "apicast-production" "apicast-staging" "apicast-wildcard-router" "backend-cron" "backend-listener" "backend-redis" "backend-worker" "system-app" "system-memcache" "system-mysql" "system-redis" "system-resque" "system-sidekiq" "system-sphinx" "zync" "zync-que" "zync-database")

NOW=$(date +"%Y-%m-%d_%H-%M" -u)

DUMP_DIR="${CURRENT_DIR}/3scale_dump-${NOW}"

# using hardcoded filename is safe now since all output files are now inside a new unique temp dir
DUMP_FILE="3scale-dump.tar"


REDACT_SCRIPT="/usr/local/bin/redact_env_vars.py"

#############
# Functions #
#############

print_error() {
    if [[ -z ${MSG} ]]; then
        echo -e "\n# Unknown Error #\n"

    else
        echo -e "\n# [Error] ${MSG} #\n"
    fi

    exit 1
}

create_dir() {
    if [[ -z ${NEWDIR} ]]; then
        MSG="Variable Not Found: NEWDIR"
        print_error

    elif [[ -z ${SINGLE_FILE} ]]; then
        MSG="Variable Not Found: SINGLE_FILE"
        print_error

    else
        if [[ ! -d ${DUMP_DIR}/${NEWDIR} ]]; then
            MKDIR=$(mkdir -pv ${DUMP_DIR}/${NEWDIR} 2>&1)
            echo -e "\t${MKDIR}"

            if [[ ! -d ${DUMP_DIR}/${NEWDIR} ]]; then
                MSG="Unable to create: ${DUMP_DIR}/${NEWDIR}"
                print_error
            fi

        elif [[ -f ${DUMP_DIR}/${SINGLE_FILE} ]]; then
            REMOVE=$(/bin/rm -fv ${DUMP_DIR}/${SINGLE_FILE} 2>&1)
            echo -e "\t${REMOVE}"

            if [[ -f ${SINGLE_FILE} ]]; then
                MSG="Unable to delete: ${DUMP_DIR}/${SINGLE_FILE}"
                print_error
            fi
        fi
    fi
}

execute_command() {
    if [[ -z ${COMMAND} ]]; then
        MSG="Variable Not Found: COMMAND"
        print_error

    elif [[ ${RESTRICT} == 1 ]]; then
        ${COMMAND} | grep -i "${THREESCALE_PROJECT}" 2> ${DUMP_DIR}/temp-cmd.txt | awk '{print $1}' > ${DUMP_DIR}/temp.txt

        detect_error

    else
        ${COMMAND} 2> ${DUMP_DIR}/temp-cmd.txt | awk '{print $1}' | tail -n +2 > ${DUMP_DIR}/temp.txt

        detect_error
    fi
}

detect_error() {
    if [[ -f ${DUMP_DIR}/temp-cmd.txt ]]; then
        TEMP_CMD=$(< ${DUMP_DIR}/temp-cmd.txt)

        if [[ -n ${TEMP_CMD} ]]; then
            echo -e "Error on the Step ${STEP} (${STEP_DESC}):\n" >> ${DUMP_DIR}/errors.txt
            cat ${DUMP_DIR}/temp-cmd.txt >> ${DUMP_DIR}/errors.txt
            echo -e "\n" >> ${DUMP_DIR}/errors.txt
        fi

        /bin/rm -f ${DUMP_DIR}/temp-cmd.txt

        unset TEMP_CMD
    fi
}

read_obj() {
    if [[ -z ${NOYAML} ]]; then
        YAML="-o yaml"
        INLINE_FILTER="| ${REDACT_SCRIPT}"
    else
        unset YAML
        unset INLINE_FILTER
    fi

    while read OBJ; do
        if [[ ! ${VALIDATE_PODS} == 1 ]]; then
            FOUND=1

        else
            FOUND=0

            for POD in "${THREEESCALE_PODS[@]}"; do
                if ( [[ ${SUBSTRING} == 1 ]] && [[ "${OBJ}" == *"${POD}"* ]] ) || ( [[ "${OBJ}" == "${POD}" ]] ); then
                    FOUND=1
                fi
            done
        fi

        if [[ ! ${FOUND} == 1 ]]; then
            echo -e "\tSkipping: ${OBJ}"

        else
            if [[ ${VERBOSE} == 1 ]]; then
                echo -e "\n\tProcess: ${OBJ}"
            fi

            if [[ ${COMPRESS} == 1 ]]; then
                CONTAINERS=$(${COMMAND} ${OBJ} --template='{{range .spec.containers}}{{.name}}
{{end}}')

                for CONTAINER in ${CONTAINERS}; do
                    if [[ ${PREVIOUS} == 1 ]]; then

                        oc logs -p ${OBJ} --container=${CONTAINER} --timestamps > ${DUMP_DIR}/${NEWDIR}/previous-temp.txt 2>&1

                        VALIDATE=$(< ${DUMP_DIR}/${NEWDIR}/previous-temp.txt head -n 1)

                        if [[ ! "${VALIDATE,,}" == *"previous terminated container"* ]] && [[ ! "${VALIDATE,,}" == *"not found"* ]]; then
                            cat ${DUMP_DIR}/${NEWDIR}/previous-temp.txt | ${COMPRESS_UTIL} -f - > ${DUMP_DIR}/${NEWDIR}/${OBJ}-${CONTAINER}.${COMPRESS_FORMAT}

                        else
                            echo -e "\n${VALIDATE}" >> ${DUMP_DIR}/${NEWDIR}/ignored-temp.txt
                        fi

                    else
                        oc logs ${OBJ} --container=${CONTAINER} --timestamps 2>&1 | ${COMPRESS_UTIL} -f - > ${DUMP_DIR}/${NEWDIR}/${OBJ}-${CONTAINER}.${COMPRESS_FORMAT}
                    fi
                done

                sleep 1.0

            else
                eval ${COMMAND} ${OBJ} ${YAML} ${INLINE_FILTER} >> ${DUMP_DIR}/${SINGLE_FILE} 2>&1
                eval ${COMMAND} ${OBJ} ${YAML} ${INLINE_FILTER} > ${DUMP_DIR}/${NEWDIR}/${OBJ}.yaml 2>&1

                sleep 0.5
            fi

        fi

    done < ${DUMP_DIR}/temp.txt

    if [[ ${PREVIOUS} == 1 ]]; then
        /bin/rm -f ${DUMP_DIR}/${NEWDIR}/previous-temp.txt

        if [[ -f ${DUMP_DIR}/${NEWDIR}/ignored-temp.txt ]]; then
            echo -e "The following containers have been ignored as there were no previous logs:\n" > ${DUMP_DIR}/${NEWDIR}/ignored-containers.txt
            cat ${DUMP_DIR}/${NEWDIR}/ignored-temp.txt >> ${DUMP_DIR}/${NEWDIR}/ignored-containers.txt

            /bin/rm -f ${DUMP_DIR}/${NEWDIR}/ignored-temp.txt
        fi
    fi

    /bin/rm -f ${DUMP_DIR}/temp.txt
}

mgmt_api() {
    if [[ -z ${OUTPUT} ]]; then
        MSG="Variable Not Found: OUTPUT"
        print_error

    elif [[ -z ${APICAST_POD} ]]; then
        MSG="Variable Not Found: APICAST_POD"
        print_error

    elif [[ ${MGMT_API,,} == "debug" ]] || [[ ${MGMT_API,,} == "status" ]]; then
        OUTPUT="${OUTPUT}-status"

        timeout 15 oc rsh ${APICAST_POD} /bin/bash -c "curl -X GET http://localhost:8090/status/live" > ${OUTPUT}-live.txt 2>&1 < /dev/null
        timeout 15 oc rsh ${APICAST_POD} /bin/bash -c "curl -X GET http://localhost:8090/status/ready" > ${OUTPUT}-ready.txt 2>&1 < /dev/null
        timeout 15 oc rsh ${APICAST_POD} /bin/bash -c "curl -X GET http://localhost:8090/status/info" > ${OUTPUT}-info.txt 2>&1 < /dev/null

        if [[ ${MGMT_API,,} == "debug" ]]; then
            OUTPUT="${OUTPUT}-debug"

            timeout 15 oc rsh ${APICAST_POD} /bin/bash -c "curl -X GET -H 'Accept: application/json' http://localhost:8090/config" > ${OUTPUT}.json 2> ${OUTPUT}-stderr.txt < /dev/null
        fi

        unset OUTPUT APICAST_POD MGMT_API
    fi
}

cleanup() {
    unset COMMAND COMPRESS NEWDIR NOYAML PREVIOUS RESTRICT SINGLE_FILE SUBSTRING VALIDATE_PODS VERBOSE
}

cleanup_dir() {
    if [[ -z ${TARGET_DIR} ]]; then
        MSG="Variable Not Found: TARGET_DIR"
        print_error

    else
        if [[ ${TARGET_DIR,,} == "dump_dir" ]]; then
            TARGET_DIR="${DUMP_DIR}"
        else
            TARGET_DIR="${DUMP_DIR}/${TARGET_DIR}"
        fi

        if [[ ${COMPRESS} == 1 ]]; then
            CMD_OUTPUT=$(/bin/rm -fv ${TARGET_DIR}/*.${COMPRESS_FORMAT} 2>&1)
            TAB=2

            display_verbose

        else
            CMD_OUTPUT=$(/bin/rm -fv ${TARGET_DIR}/{*.txt,*.json,*.yml,*.yaml} 2>&1)
            TAB=2

            display_verbose
        fi

        RMDIR=$(rmdir -v ${TARGET_DIR} 2>&1)

        echo -e "\n\t${RMDIR}\n"

        sleep 0.25
    fi

    unset TARGET_DIR COMPRESS
}

display_verbose() {
    while read ITEM; do
        if [[ ${TAB} == 2 ]]; then
            echo -e "\t\t${ITEM}"

        elif [[ ${TAB} == 1 ]]; then
            echo -e "\t${ITEM}"

        else
            echo -e "${ITEM}"
        fi
    done <<< "${CMD_OUTPUT}"

    unset TAB
}

print_step() {
    echo -e "\n${STEP}. ${STEP_DESC}\n"
}

fetch_nodes() {
    if [[ ${FIRST_CHECK} == 1 ]]; then
        FETCH_NODES_DIR="status/nodes-before"

    else
        FETCH_NODES_DIR="status/nodes-after"

    fi

    # YAML format

    NEWDIR="${FETCH_NODES_DIR}"
    SINGLE_FILE="${FETCH_NODES_DIR}.yaml"
    COMMAND="oc get nodes -o wide"

    create_dir
    execute_command
    read_obj
    cleanup

    # TXT (describe) format

    oc get nodes -o wide --show-kind --show-labels > ${DUMP_DIR}/${FETCH_NODES_DIR}.txt 2>&1

    COMMAND="oc get nodes -o wide"
    execute_command

    while read NODE; do
        DESCRIBE=$(oc describe node ${NODE} 2> ${DUMP_DIR}/temp-cmd.txt)
        detect_error

        echo -e "${DESCRIBE}" > ${DUMP_DIR}/${FETCH_NODES_DIR}/${NODE}.txt
        echo -e "${DESCRIBE}\n" >> ${DUMP_DIR}/${FETCH_NODES_DIR}-describe.txt

        sleep 0.5

    done < ${DUMP_DIR}/temp.txt
}


########
# MAIN #
########


# Validate Argument: 3scale project #

if [[ -z ${THREESCALE_PROJECT} ]]; then
    MSG="Usage: 3scale_dump.sh [3SCALE PROJECT] [COMPRESS UTIL (Optional)]"
    print_error

else

    # Validate the existance of the project
    OC_PROJECT_DEBUG=$(oc get project 2>&1)
    OC_PROJECT=$(echo -e "${OC_PROJECT_DEBUG}" | awk '{print $1}' | grep -iw "${THREESCALE_PROJECT}" | sort | head -n 1)

    if [[ ! "${OC_PROJECT}" == "${THREESCALE_PROJECT}" ]]; then
        MSG="Project not found: ${THREESCALE_PROJECT}:\n\n~~~\n${OC_PROJECT_DEBUG}\n~~~\n\nEnsure that you are logged in and specified the correct project"
        print_error

    else
        # Change to the 3scale project
        echo
        oc project ${THREESCALE_PROJECT}
    fi
fi


# Validate Argument: Compress Util #

# Attempt to auto-detect the COMPRESS_UTIL if not specified

if [[ -z ${COMPRESS_UTIL} ]] || [[ "${COMPRESS_UTIL}" == "auto" ]] || [[ ${COMPRESS_UTIL} == "xz" ]]; then
    XZ_COMMAND=$(command -v xz 2>&1)

    XZ_VERSION=$(xz --version 2>&1)

    if [[ -n ${XZ_COMMAND} ]] && [[ "${XZ_VERSION,,}" == *"xz utils"* ]]; then
        echo -e "\nXZ util found:\n\n~~~\n${XZ_VERSION}\n~~~\n"
        COMPRESS_UTIL="xz"
        COMPRESS_FORMAT="${COMPRESS_UTIL}"

    else
        echo -e "\nXZ util not found: using gzip\n"
        COMPRESS_UTIL="gzip"
        COMPRESS_FORMAT="gz"
    fi

elif [[ ${COMPRESS_UTIL} == "gz" ]] || [[ ${COMPRESS_UTIL} == "gzip" ]]; then
    COMPRESS_UTIL="gzip"
    COMPRESS_FORMAT="gz"

else
    MSG="Invalid Compress Util: ${COMPRESS_UTIL} (Values: gzip, xz)"
    print_error
fi

# The block of lines commented with ### below have been removed to allow script to be run non-interactively by tiered access via devaccess_wrap.py
###
### # Validate: Permissions
###
### FORBIDDEN=$(oc describe node 2>&1 | grep -i "forbidden")
###
### if [[ -n ${FORBIDDEN} ]]; then
###     echo -e "\nWARNING: It looks like the Red Hat 3scale dump is being executed with an OpenShift user that doesn't have the 'cluster-admin' role. While the information fetched could be already sufficient to troubleshoot the issue regardless of this limitation, it's recommended using elevated privileges if possible (otherwise, please go ahead and proceed anyway). Refer to the section 'Administrator (Recommended)' from the Knowledge Base Article for more information. \n\nPress [ENTER] to continue or <Ctrl + C> to abort...\n"
###     read TEMP < /dev/tty
### fi
###
###
### # Case Number
###
### echo -ne "Please enter the number of the Red Hat Case which this dump belongs to (Optional): "
### read CASE < /dev/tty
###
### if [[ -n ${CASE} ]]; then
###     echo -e "\nCase: ${CASE}.\n"
###
###     DUMP_DIR="${CURRENT_DIR}/${CASE}-3scale_dump-${NOW}"
###
###     DUMP_FILE="${DUMP_DIR}.tar"
###
### else
###     echo -e "\nNOTE: No Case has been specified. Proceeding anyway.\n"
### fi
###
###
### echo -e "NOTE: A temporary directory will be created in order to store the information about the 3scale dump: ${DUMP_DIR}\n\nPress [ENTER] to continue or <Ctrl + C> to abort...\n"
### read TEMP < /dev/tty


# Create the Dump Directory if it does not exist #

if [[ ! -d ${DUMP_DIR}/status/apicast-staging ]] || [[ ! -d ${DUMP_DIR}/status/apicast-production ]]; then
    CMD_OUTPUT=$(mkdir -pv ${DUMP_DIR}/status/{apicast-staging,apicast-production} 2>&1)
    TAB=1

    display_verbose

    if [[ ! -d ${DUMP_DIR}/status/apicast-staging ]] || [[ ! -d ${DUMP_DIR}/status/apicast-production ]]; then
        MSG="Unable to create: ${DUMP_DIR}/status"
        print_error
    fi
fi

STEP=1


# Status: Nodes (First Check) #

STEP_DESC="Status: Nodes (First Check)"
print_step

FIRST_CHECK=1

fetch_nodes

((STEP++))


# Fetch the status from all the pods and events #

STEP_DESC="Fetch: All pods and Events"
print_step

oc get pod -o wide > ${DUMP_DIR}/status/pods-all.txt 2>&1

oc get pod -o wide --all-namespaces > ${DUMP_DIR}/status/pods-all-namespaces.txt 2>&1

oc get pod -o wide | grep -iv "deploy" > ${DUMP_DIR}/status/pods.txt 2>&1

oc get pod -o wide | grep -i "deploy" > ${DUMP_DIR}/status/pods-deploy.txt 2>&1

oc get event > ${DUMP_DIR}/status/events.txt 2>&1

oc version > ${DUMP_DIR}/status/ocp-version.txt 2>&1

((STEP++))


# DeploymentConfig objects #

STEP_DESC="Fetch: DeploymentConfig"
print_step

NEWDIR="dc"
SINGLE_FILE="dc.yaml"
COMMAND="oc get dc"

VALIDATE_PODS=1

create_dir
execute_command
read_obj
cleanup

((STEP++))


# Fetch and compress the logs #

STEP_DESC="Fetch: Logs"
print_step

NEWDIR="logs"
SINGLE_FILE="logs.txt"
COMMAND="oc get pod"

VALIDATE_PODS=1
SUBSTRING=1
COMPRESS=1
VERBOSE=1
NOYAML=1

cat ${DUMP_DIR}/status/pods.txt | awk '{print $1}' | tail -n +2 > ${DUMP_DIR}/temp.txt

create_dir
read_obj
cleanup

echo -e "\n\n\t# Logs from previous pods (if any) #\n"


# Previous logs #

NEWDIR="logs/previous"
SINGLE_FILE="logs-previous.txt"
COMMAND="oc get pod"

VALIDATE_PODS=1
SUBSTRING=1
COMPRESS=1
VERBOSE=1
NOYAML=1
PREVIOUS=1

cat ${DUMP_DIR}/status/pods.txt | awk '{print $1}' | tail -n +2 > ${DUMP_DIR}/temp.txt

create_dir
read_obj
cleanup


# Build the shell script to uncompress all logs according to the util (gzip, xz) being used

if [[ ${COMPRESS_UTIL} == "xz" ]]; then
    echo -e '#!/bin/bash\n\nfor FILE in *.xz; do\n\txz -d ${FILE}\n\ndone' > ${DUMP_DIR}/logs/uncompress-logs.sh
    echo -e '#!/bin/bash\n\nfor FILE in *.xz; do\n\txz -d ${FILE}\n\ndone' > ${DUMP_DIR}/logs/previous/uncompress-logs.sh

else
    echo -e '#!/bin/bash\n\nfor FILE in *.gz; do\n\tgunzip ${FILE}\n\ndone' > ${DUMP_DIR}/logs/uncompress-logs.sh
    echo -e '#!/bin/bash\n\nfor FILE in *.gz; do\n\tgunzip ${FILE}\n\ndone' > ${DUMP_DIR}/logs/previous/uncompress-logs.sh
fi

chmod +x ${DUMP_DIR}/logs/uncompress-logs.sh

chmod +x ${DUMP_DIR}/logs/previous/uncompress-logs.sh


# Fetch the logs from the pods in the 'deploy' state (if any):

DEPLOY_PODS=$(oc get pod -o wide | grep -i "deploy" 2> /dev/null)

if [[ -n ${DEPLOY_PODS} ]]; then

    echo -e "\n\n\t# Logs from pods in a 'deploy' state #\n"

    NEWDIR="logs/deploy"
    SINGLE_FILE="logs-deploy.txt"
    COMMAND="oc get pod"

    VALIDATE_PODS=1
    SUBSTRING=1
    COMPRESS=1
    VERBOSE=1
    NOYAML=1

    cat ${DUMP_DIR}/status/pods-deploy.txt | awk '{print $1}' > ${DUMP_DIR}/temp.txt

    create_dir
    read_obj
    cleanup

    if [[ ${COMPRESS_UTIL} == "xz" ]]; then
        echo -e '#!/bin/bash\n\nfor FILE in *.xz; do\n\txz -d ${FILE}\n\ndone' > ${DUMP_DIR}/logs/deploy/uncompress-logs.sh

    else
        echo -e '#!/bin/bash\n\nfor FILE in *.gz; do\n\tgunzip ${FILE}\n\ndone' > ${DUMP_DIR}/logs/deploy/uncompress-logs.sh
    fi

    chmod +x ${DUMP_DIR}/logs/deploy/uncompress-logs.sh
fi

((STEP++))


# The block of lines commented with ### below have been removed for security concerns when 3scale dump is being run via rhmi_3scale_dump tiered access command
### # Secrets #
### 
### STEP_DESC="Fetch: Secrets"
### print_step
### 
### NEWDIR="secrets"
### SINGLE_FILE="secrets.yaml"
### COMMAND="oc get secret"
### 
### create_dir
### execute_command
### read_obj
### cleanup
### 
### ((STEP++))


# Routes #

STEP_DESC="Fetch: Routes"
print_step

NEWDIR="routes"
SINGLE_FILE="routes.yaml"
COMMAND="oc get route"

create_dir
execute_command
read_obj
cleanup

((STEP++))


# Services #

STEP_DESC="Fetch: Services"
print_step

NEWDIR="services"
SINGLE_FILE="services.yaml"
COMMAND="oc get service"

create_dir
execute_command
read_obj
cleanup

((STEP++))


# Image Streams #

STEP_DESC="Fetch: Image Streams"
print_step

NEWDIR="images"
SINGLE_FILE="images.yaml"
COMMAND="oc get imagestream"

create_dir
execute_command
read_obj
cleanup

((STEP++))


# ConfigMaps #

STEP_DESC="Fetch: ConfigMaps"
print_step

NEWDIR="configmaps"
SINGLE_FILE="configmaps.yaml"
COMMAND="oc get configmap"

create_dir
execute_command
read_obj
cleanup

((STEP++))


# PV #

STEP_DESC="Fetch: PV"
print_step

NEWDIR="pv"
SINGLE_FILE="pv.yaml"
COMMAND="oc get pv"
RESTRICT=1

${COMMAND} | grep -i "${THREESCALE_PROJECT}" > ${DUMP_DIR}/status/pv.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

create_dir
execute_command
read_obj
cleanup

NEWDIR="pv/describe"
SINGLE_FILE="pv/describe.txt"
COMMAND="oc get pv"
RESTRICT=1

create_dir
execute_command
cleanup

while read PV; do
    DESCRIBE=$(oc describe pv ${PV} 2> ${DUMP_DIR}/temp-cmd.txt)
    detect_error

    echo -e "${DESCRIBE}" > ${DUMP_DIR}/pv/describe/${PV}.txt
    echo -e "${DESCRIBE}\n" >> ${DUMP_DIR}/pv/describe.txt

    sleep 0.5

done < ${DUMP_DIR}/temp.txt

((STEP++))


# PVC #

STEP_DESC="Fetch: PVC"
print_step

NEWDIR="pvc"
SINGLE_FILE="pvc.yaml"
COMMAND="oc get pvc"

${COMMAND} > ${DUMP_DIR}/status/pvc.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

create_dir
execute_command
read_obj
cleanup

NEWDIR="pvc/describe"
SINGLE_FILE="pvc/describe.txt"
COMMAND="oc get pvc"

create_dir
execute_command
cleanup

while read PVC; do
    DESCRIBE=$(oc describe pvc ${PVC} 2> ${DUMP_DIR}/temp-cmd.txt)
    detect_error

    echo -e "${DESCRIBE}" > ${DUMP_DIR}/pvc/describe/${PVC}.txt
    echo -e "${DESCRIBE}\n" >> ${DUMP_DIR}/pvc/describe.txt

    sleep 0.5

done < ${DUMP_DIR}/temp.txt

((STEP++))


# ServiceAccounts #

STEP_DESC="Fetch: ServiceAccounts"
print_step

NEWDIR="serviceaccounts"
SINGLE_FILE="serviceaccounts.yaml"
COMMAND="oc get serviceaccount"

create_dir
execute_command
read_obj
cleanup

((STEP++))


# Status: Replication Controllers #

STEP_DESC="Status: Replication Controllers"
print_step

# YAML format

NEWDIR="status/replicationcontrollers"
SINGLE_FILE="status/replicationcontrollers.yaml"
COMMAND="oc get replicationcontrollers -o wide"

create_dir
execute_command
read_obj
cleanup

# TXT (describe) format

COMMAND="oc get replicationcontrollers -o wide"
execute_command

${COMMAND} > ${DUMP_DIR}/status/replicationcontrollers.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

while read RC; do
    DESCRIBE=$(oc describe replicationcontroller ${RC} 2> ${DUMP_DIR}/temp-cmd.txt)
    detect_error

    echo -e "${DESCRIBE}" > ${DUMP_DIR}/status/replicationcontrollers/${RC}.txt

    sleep 0.1

done < ${DUMP_DIR}/temp.txt

((STEP++))


# Status: Project Quotas #

STEP_DESC="Status: Quotas"
print_step

oc get quota -o yaml > ${DUMP_DIR}/status/quotas.yaml 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

oc describe quota > ${DUMP_DIR}/status/quotas.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

((STEP++))


# Status: Limits #

STEP_DESC="Status: Limits"
print_step

cat ${DUMP_DIR}/status/pods-all.txt | awk '{print $1}' | tail -n +2 > ${DUMP_DIR}/temp.txt

LIMITS_DESCRIBE_FILE="${DUMP_DIR}/temp-describe.txt"
LIMITS_FILE="${DUMP_DIR}/limits-temp.txt"

while read POD; do

    echo -e "\n\tProcess: ${POD}"

    oc describe pod "${POD}" > ${LIMITS_DESCRIBE_FILE}

    while read LINE; do

        if [[ "${LINE,,}" == *"container id:"* ]] && [[ ! "${PREVIOUS_LINE,,}" == *"-svc:"* ]]; then
            PREVIOUS_LINE=$(echo "${PREVIOUS_LINE}" | sed "s@:@@g")

            echo -e "\n\n# Pod: ${POD} | Container: ${PREVIOUS_LINE} #\n" >> ${LIMITS_FILE}

        elif [[ "${LINE,,}" == *"limits"* ]]; then
            echo -e "${LINE}" >> ${LIMITS_FILE}

        elif [[ "${LINE,,}" == *"requests:"* ]]; then
            echo -e "\n${LINE}" >> ${LIMITS_FILE}

        elif [[ "${LINE,,}" == *"cpu:"* ]] || [[ "${LINE,,}" == *"memory:"* ]]; then
            echo -e "  ${LINE}" >> ${LIMITS_FILE}

        fi

        PREVIOUS_LINE="${LINE}"

    done < ${LIMITS_DESCRIBE_FILE}

    sleep 1.0

done < ${DUMP_DIR}/temp.txt

cat ${LIMITS_FILE} | tail -n +3 > ${DUMP_DIR}/status/limits.txt

/bin/rm -f ${LIMITS_DESCRIBE_FILE} ${LIMITS_FILE}

((STEP++))


# Status: OpenShift Project Debug #

STEP_DESC="Status: OpenShift Project Debug"
print_step

echo -e "# Overall Status #\n" > ${DUMP_DIR}/status/openshift-status.txt

oc status >> ${DUMP_DIR}/status/openshift-status.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

echo -e "\n\n# Suggestions #\n" >> ${DUMP_DIR}/status/openshift-status.txt

oc status --suggest >> ${DUMP_DIR}/status/openshift-status.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

echo -e "\n\n# Dot Output #\n" >> ${DUMP_DIR}/status/openshift-status.txt

oc status -o dot >> ${DUMP_DIR}/status/openshift-status.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

((STEP++))


# Status: Host Subnet #

STEP_DESC="Status: Host Subnet"
print_step

oc get hostsubnet -o yaml > ${DUMP_DIR}/status/hostsubnet.yaml 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

oc get hostsubnet > ${DUMP_DIR}/status/hostsubnet.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

echo -e "\n" >> ${DUMP_DIR}/status/hostsubnet.txt

oc describe hostsubnet >> ${DUMP_DIR}/status/hostsubnet.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

((STEP++))


# Status: SCC #

STEP_DESC="Status: SCC"
print_step

oc get scc -o yaml > ${DUMP_DIR}/status/scc.yaml 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

oc get scc > ${DUMP_DIR}/status/scc.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

echo -e "\n" >> ${DUMP_DIR}/status/scc.txt

oc describe scc >> ${DUMP_DIR}/status/scc.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

((STEP++))


# Status: (Cluster) Role Binding #

STEP_DESC="Status: (Cluster) Role Binding"
print_step

oc get rolebinding -o yaml > ${DUMP_DIR}/status/rolebinding.yaml 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

oc get rolebinding > ${DUMP_DIR}/status/rolebinding.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

echo -e "\n" >> ${DUMP_DIR}/status/rolebinding.txt

oc describe rolebinding >> ${DUMP_DIR}/status/rolebinding.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error


oc get clusterrolebinding -o yaml > ${DUMP_DIR}/status/rolebinding-cluster.yaml 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

oc get clusterrolebinding > ${DUMP_DIR}/status/rolebinding-cluster.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

echo -e "\n" >> ${DUMP_DIR}/status/rolebinding-cluster.txt

oc describe clusterrolebinding >> ${DUMP_DIR}/status/rolebinding-cluster.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

((STEP++))


# Status: Storage Class #

STEP_DESC="Status: Storage Class"
print_step

oc get storageclass -o yaml > ${DUMP_DIR}/status/storageclass.yaml 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

oc get storageclass -o wide > ${DUMP_DIR}/status/storageclass.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

echo -e "\n" >> ${DUMP_DIR}/status/scc.txt

oc describe storageclass >> ${DUMP_DIR}/status/storageclass.txt 2> ${DUMP_DIR}/temp-cmd.txt
detect_error

((STEP++))


# Variables used on the next steps #

APICAST_POD_STG=$(oc get pod | grep -i "apicast-staging" | grep -i "running" | grep -iv "deploy" | head -n 1 | awk '{print $1}')

if [[ -n ${APICAST_POD_STG} ]]; then
    MGMT_API_STG=$(oc rsh ${APICAST_POD_STG} /bin/bash -c "env | grep 'APICAST_MANAGEMENT_API=' | head -n 1 | cut -d '=' -f 2" < /dev/null)
    APICAST_ROUTE_STG=$(oc get route | grep -i "apicast-staging" | grep -v NAME | head -n 1 | awk '{print $2}')
    THREESCALE_PORTAL_ENDPOINT=$(oc rsh ${APICAST_POD_STG} /bin/bash -c "env | grep 'THREESCALE_PORTAL_ENDPOINT=' | head -n 1 | cut -d '=' -f 2" < /dev/null)

    sleep 0.5
fi


APICAST_POD_PRD=$(oc get pod | grep -i "apicast-production" | grep -i "running" | grep -iv "deploy" | head -n 1 | awk '{print $1}')

if [[ -n ${APICAST_POD_PRD} ]]; then
    MGMT_API_PRD=$(oc rsh ${APICAST_POD_PRD} /bin/bash -c "env | grep 'APICAST_MANAGEMENT_API=' | head -n 1 | cut -d '=' -f 2" < /dev/null)
    APICAST_ROUTE_PRD=$(oc get route | grep -i "apicast-production" | grep -v NAME | head -n 1 | awk '{print $2}')

    if [[ -z ${THREESCALE_PORTAL_ENDPOINT} ]]; then
        THREESCALE_PORTAL_ENDPOINT=$(oc rsh ${APICAST_POD_PRD} /bin/bash -c "env | grep 'THREESCALE_PORTAL_ENDPOINT=' | head -n 1 | cut -d '=' -f 2" < /dev/null)
    fi

    sleep 0.5
fi


WILDCARD_POD=$(oc get pod | grep -i "apicast-wildcard-router" | grep -i "running" | grep -iv "deploy" | grep -v NAME | head -n 1 | awk '{print $1}')

SYSTEM_APP_POD=$(oc get pod | grep -i "system-app" | grep -i "running" | grep -iv "deploy" | head -n 1 | awk '{print $1}')

echo -e "\n# Variables used in the next following steps #\n\n\tAPICAST_POD_PRD: ${APICAST_POD_PRD}\n\tAPICAST_POD_STG: ${APICAST_POD_STG}\n\tMGMT_API_PRD: ${MGMT_API_PRD}\n\tMGMT_API_STG: ${MGMT_API_STG}\n\tAPICAST_ROUTE_PRD: ${APICAST_ROUTE_PRD}\n\tAPICAST_ROUTE_STG: ${APICAST_ROUTE_STG}\n\tWILDCARD POD: ${WILDCARD_POD}\n\tTHREESCALE_PORTAL_ENDPOINT: ${THREESCALE_PORTAL_ENDPOINT}\n\tSYSTEM_APP_POD: ${SYSTEM_APP_POD}" | tee ${DUMP_DIR}/status/3scale-variables.txt

sleep 3


# Build the shell script to filter the Staging and Production JSON's from single line to multiple lines

echo -e '#!/bin/bash\n\nfor FILE in *.json; do\n\tpython -m json.tool ${FILE} > ${FILE}.filtered ; sleep 0.5 ; mv -f ${FILE}.filtered ${FILE}\n\ndone' > ${DUMP_DIR}/status/apicast-staging/python-json.sh
chmod +x ${DUMP_DIR}/status/apicast-staging/python-json.sh

echo -e '#!/bin/bash\n\nfor FILE in *.json; do\n\tpython -m json.tool ${FILE} > ${FILE}.filtered ; sleep 0.5 ; mv -f ${FILE}.filtered ${FILE}\n\ndone' > ${DUMP_DIR}/status/apicast-production/python-json.sh
chmod +x ${DUMP_DIR}/status/apicast-production/python-json.sh


# Status: 3scale Echo API #

STEP_DESC="Status: 3scale Echo API"
print_step

if [[ -n ${APICAST_POD_STG} ]]; then
    timeout 15 oc rsh ${APICAST_POD_STG} /bin/bash -c "curl -k -vvv https://echo-api.3scale.net" > ${DUMP_DIR}/status/apicast-staging/3scale-echo-api-staging.txt 2>&1 < /dev/null

    sleep 0.5
fi

if [[ -n ${APICAST_POD_PRD} ]]; then
    timeout 15 oc rsh ${APICAST_POD_PRD} /bin/bash -c "curl -k -vvv https://echo-api.3scale.net" > ${DUMP_DIR}/status/apicast-production/3scale-echo-api-production.txt 2>&1 < /dev/null

    sleep 0.5
fi

((STEP++))


# Status: Staging/Production Backend JSON #

STEP_DESC="Status: Staging/Production Backend JSON"
print_step

if [[ -n ${APICAST_POD_STG} ]] && [[ -n ${SYSTEM_APP_POD} ]]; then

    timeout 15 oc rsh ${APICAST_POD_STG} /bin/bash -c "curl -X GET -H 'Accept: application/json' -k ${THREESCALE_PORTAL_ENDPOINT}/staging.json" > ${DUMP_DIR}/status/apicast-staging/staging.json 2> ${DUMP_DIR}/status/apicast-staging/apicast-staging-json-debug.txt < /dev/null

    timeout 15 oc rsh ${APICAST_POD_STG} /bin/bash -c "curl -X GET -k -vvv -k ${THREESCALE_PORTAL_ENDPOINT}/staging.json" > ${DUMP_DIR}/status/apicast-staging/staging-json-verbose.txt 2>&1 < /dev/null

    sleep 0.5

    timeout 15 oc rsh ${APICAST_POD_STG} /bin/bash -c "curl -X GET -H 'Accept: application/json' -k ${THREESCALE_PORTAL_ENDPOINT}/production.json" > ${DUMP_DIR}/status/apicast-staging/production.json 2> ${DUMP_DIR}/status/apicast-staging/apicast-production-json-debug.txt < /dev/null

    timeout 15 oc rsh ${APICAST_POD_STG} /bin/bash -c "curl -X GET -k -vvv ${THREESCALE_PORTAL_ENDPOINT}/production.json" > ${DUMP_DIR}/status/apicast-staging/production-json-verbose.txt 2>&1 < /dev/null

    sleep 0.5
fi

if [[ -n ${APICAST_POD_PRD} ]] && [[ -n ${SYSTEM_APP_POD} ]]; then

    timeout 15 oc rsh ${APICAST_POD_PRD} /bin/bash -c "curl -X GET -H 'Accept: application/json' -k ${THREESCALE_PORTAL_ENDPOINT}/staging.json" > ${DUMP_DIR}/status/apicast-production/staging.json 2> ${DUMP_DIR}/status/apicast-production/apicast-staging-json-debug.txt < /dev/null

    timeout 15 oc rsh ${APICAST_POD_STG} /bin/bash -c "curl -X GET -k -vvv -k ${THREESCALE_PORTAL_ENDPOINT}/staging.json" > ${DUMP_DIR}/status/apicast-production/staging-json-verbose.txt 2>&1 < /dev/null

    sleep 0.5

    timeout 15 oc rsh ${APICAST_POD_PRD} /bin/bash -c "curl -X GET -H 'Accept: application/json' -k ${THREESCALE_PORTAL_ENDPOINT}/production.json" > ${DUMP_DIR}/status/apicast-production/production.json 2> ${DUMP_DIR}/status/apicast-production/apicast-production-json-debug.txt < /dev/null

    timeout 15 oc rsh ${APICAST_POD_STG} /bin/bash -c "curl -X GET -k -vvv ${THREESCALE_PORTAL_ENDPOINT}/production.json" > ${DUMP_DIR}/status/apicast-production/production-json-verbose.txt 2>&1 < /dev/null

    sleep 0.5
fi

((STEP++))


# Status: Management API #

STEP_DESC="Status: Management API"
print_step

if [[ -n ${APICAST_POD_STG} ]]; then
    OUTPUT="${DUMP_DIR}/status/apicast-staging/mgmt-api"
    APICAST_POD="${APICAST_POD_STG}"
    MGMT_API="${MGMT_API_STG}"

    mgmt_api

    sleep 0.5
fi

if [[ -n ${APICAST_POD_PRD} ]]; then
    OUTPUT="${DUMP_DIR}/status/apicast-production/mgmt-api"
    APICAST_POD="${APICAST_POD_PRD}"
    MGMT_API="${MGMT_API_PRD}"

    mgmt_api

    sleep 0.5
fi

((STEP++))


# APIcast Status: APIcast Certificates #

STEP_DESC="Status: APIcast Certificates"
print_step

if [[ -n ${APICAST_POD_STG} ]] && [[ -n ${WILDCARD_POD} ]]; then
    timeout 15 oc rsh ${WILDCARD_POD} /bin/bash -c "echo -e '\n# Host: ${APICAST_ROUTE_STG} #\n' ; echo | openssl s_client -servername ${APICAST_ROUTE_STG} -connect ${APICAST_ROUTE_STG}:443" > ${DUMP_DIR}/status/apicast-staging/certificate.txt 2>&1 < /dev/null

    sleep 0.5

    timeout 15 oc rsh ${WILDCARD_POD} /bin/bash -c "echo -e '\n# Host: ${APICAST_ROUTE_STG} #\n' ; echo | openssl s_client -showcerts -servername ${APICAST_ROUTE_STG} -connect ${APICAST_ROUTE_STG}:443" > ${DUMP_DIR}/status/apicast-staging/certificate-showcerts.txt 2>&1 < /dev/null

    sleep 0.5
fi

if [[ -n ${APICAST_POD_PRD} ]] && [[ -n ${WILDCARD_POD} ]]; then
    timeout 15 oc rsh ${WILDCARD_POD} /bin/bash -c "echo -e '\n# Host: ${APICAST_ROUTE_PRD} #\n' ; echo | openssl s_client -servername ${APICAST_ROUTE_PRD} -connect ${APICAST_ROUTE_PRD}:443" > ${DUMP_DIR}/status/apicast-production/certificate.txt 2>&1 < /dev/null

    sleep 0.5

    timeout 15 oc rsh ${WILDCARD_POD} /bin/bash -c "echo -e '\n# Host: ${APICAST_ROUTE_PRD} #\n' ; echo | openssl s_client -showcerts -servername ${APICAST_ROUTE_PRD} -connect ${APICAST_ROUTE_PRD}:443" > ${DUMP_DIR}/status/apicast-production/certificate-showcerts.txt 2>&1 < /dev/null

    sleep 0.5
fi

((STEP++))


# Status: Project and Pods 'runAsUser' (Database RW issues) #

STEP_DESC="Status: Project and Pods 'runAsUser'"
print_step

oc get project ${THREESCALE_PROJECT} -o yaml > ${DUMP_DIR}/status/project.txt 2>&1

cat ${DUMP_DIR}/status/pods.txt 2>&1 | awk '{print $1}' | tail -n +2 > ${DUMP_DIR}/temp.txt

while read POD; do
    RUNASUSER=$(oc get pod ${POD} -o yaml | grep "runAsUser" | head -n 1 | cut -d ":" -f 2 | sed "s@ @@g")

    echo -e "Pod: ${POD} | RunAsUser: ${RUNASUSER}\n" >> ${DUMP_DIR}/status/pods-run-as-user.txt 2>&1

    sleep 0.5

done < ${DUMP_DIR}/temp.txt

((STEP++))


# Status: Rails Console Queries #

STEP_DESC="Status: Rails Console Queries (might take up to 3 minutes)"
print_step

if [[ -n ${SYSTEM_APP_POD} ]]; then
    timeout 180 oc rsh -c system-master ${SYSTEM_APP_POD} /bin/bash -c "echo -e 'y Account.first.domain\ny Sidekiq::Stats.new\ny AccessToken.all' | bundle exec rails console" > ${DUMP_DIR}/status/rails.txt 2>&1 < /dev/null

    sleep 1.5
fi

((STEP++))


# OCP Operator (4.X only) #

OPERATOR=$(< ${DUMP_DIR}/status/pods-all.txt grep -i "3scale-operator")

if [[ -z ${OPERATOR} ]]; then
    MSG="\n# NOTE: Ignore errors if OCP < 4.X #\n"

    echo -e "${MSG}" > ${DUMP_DIR}/status/apimanager.txt

    echo -e "${MSG}" > ${DUMP_DIR}/status/apimanager.yaml

fi

oc describe apimanager >> ${DUMP_DIR}/status/apimanager.txt 2>&1

oc get apimanager -o yaml >> ${DUMP_DIR}/status/apimanager.yaml 2>&1

((STEP++))


# Status: Nodes (Last Check) #

STEP_DESC="Status: Nodes (Last Check)"
print_step

FIRST_CHECK=0

fetch_nodes

((STEP++))


# Compact the Directory #

echo -e "\n# Compacting... #\n"

if [[ -f ${DUMP_FILE} ]]; then
    /bin/rm -f ${DUMP_FILE}

    if [[ -f ${DUMP_FILE} ]]; then
        MSG="There was an error deleting ${DUMP_FILE}"
        print_error
    fi
fi

/bin/rm -f ${DUMP_DIR}/temp.txt


# Add the .txt log file if exists #

if [[ -f ${CURRENT_DIR}/3scale-dump-logs.txt ]]; then
    /bin/cp -f ${CURRENT_DIR}/3scale-dump-logs.txt ${DUMP_DIR}/3scale-dump-logs.txt
fi

tar cpf ${DUMP_FILE} ${DUMP_DIR}

if [[ ! -f ${DUMP_FILE} ]]; then
    MSG="There was an error creating ${DUMP_FILE}"
    print_error

else
    # Cleanup (less aggressive than "rm -fr ...") #

    echo -e "\n# Cleanup... #\n"

    sleep 3

    REMOVE=$(/bin/rm -fv ${DUMP_DIR}/status/apicast-staging/python-json.sh 2>&1)
    echo -e "\t\t${REMOVE}"

    TARGET_DIR="status/apicast-staging"
    cleanup_dir

    REMOVE=$(/bin/rm -fv ${DUMP_DIR}/status/apicast-production/python-json.sh 2>&1)
    echo -e "\t\t${REMOVE}"

    TARGET_DIR="status/apicast-production"
    cleanup_dir

    TARGET_DIR="status/nodes-before"
    cleanup_dir

    TARGET_DIR="status/nodes-after"
    cleanup_dir

    TARGET_DIR="status/replicationcontrollers"
    cleanup_dir

    TARGET_DIR="status"
    cleanup_dir

    TARGET_DIR="dc"
    cleanup_dir

    REMOVE=$(/bin/rm -fv ${DUMP_DIR}/logs/previous/uncompress-logs.sh 2>&1)
    echo -e "\t\t${REMOVE}"

    if [[ -f ${DUMP_DIR}/logs/previous/ignored-containers.txt ]]; then
        REMOVE=$(/bin/rm -fv ${DUMP_DIR}/logs/previous/ignored-containers.txt 2>&1)
        echo -e "\t\t${REMOVE}"
    fi

    TARGET_DIR="logs/previous"
    COMPRESS=1
    cleanup_dir

    if [[ -n ${DEPLOY_PODS} ]]; then
        REMOVE=$(/bin/rm -fv ${DUMP_DIR}/logs/deploy/uncompress-logs.sh 2>&1)
        echo -e "\t\t${REMOVE}"

        TARGET_DIR="logs/deploy"
        COMPRESS=1
        cleanup_dir
    fi

    REMOVE=$(/bin/rm -fv ${DUMP_DIR}/logs/uncompress-logs.sh 2>&1)
    echo -e "\t\t${REMOVE}"

    TARGET_DIR="logs"
    COMPRESS=1
    cleanup_dir

    TARGET_DIR="secrets"
    cleanup_dir

    TARGET_DIR="routes"
    cleanup_dir

    TARGET_DIR="services"
    cleanup_dir

    TARGET_DIR="images"
    cleanup_dir

    TARGET_DIR="configmaps"
    cleanup_dir

    TARGET_DIR="pv/describe"
    cleanup_dir

    TARGET_DIR="pv"
    cleanup_dir

    TARGET_DIR="pvc/describe"
    cleanup_dir

    TARGET_DIR="pvc"
    cleanup_dir

    TARGET_DIR="serviceaccounts"
    cleanup_dir

    TARGET_DIR="dump_dir"
    cleanup_dir

    echo -e "\nFile created: ${DUMP_FILE}\n"

    if [[ -d ${DUMP_DIR} ]]; then
        echo -e "\nPlease remove manually the temporary directory: ${DUMP_DIR}\n"
    fi

    exit 0
fi
