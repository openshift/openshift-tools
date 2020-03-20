#!/bin/bash

THREESCALE_DUMP_SCRIPT_URL=https://raw.githubusercontent.com/jessesarn/3scaledump/master/3scale-dump.sh
THREESCALE_DUMP_SCRIPT=3scale-dump.sh
OUTPUT_FILE=3scale-dump.tar

cat << EOF >&2
***WARNING***

The output tarball created by the 3scale dump will be returned directly to stdout
Failure to redirect stdout to file will result in a multi megabyte binary file to
write to your terminal display which will be useless and require the script to be run again

Example:

  $ ssh devaccess@<master_public_ip> rhmi_3scale_dump.sh > ~/3scale-dump-for-CASE-nnnnnn.tar"

If you want to check/fix your command, hit ctrl+c to abort; otherwise, script will resume in:

EOF

for i in {5..1}; do
  echo "... $i" >&2
  sleep 1
done

TEMP_DIR=$(mktemp -d)

pushd $TEMP_DIR > /dev/null

# Download dump script and set executable
curl -s ${THREESCALE_DUMP_SCRIPT_URL} -o ${THREESCALE_DUMP_SCRIPT}
chmod +x ${THREESCALE_DUMP_SCRIPT}

echo "Creating new 3scale dump bundle" >&2

# Run the 3scale dump script, redirecting its stdout to stderr (this allows status progress to report w/o tainting stdout output file stream)
./${THREESCALE_DUMP_SCRIPT} openshift-3scale 1>&2

# Copy output file directly to stdout stream
echo "Streaming output file to stdout..." >&2
cp ${OUTPUT_FILE} /dev/stdout

# cleanup script/output files
rm ${OUTPUT_FILE} ${THREESCALE_DUMP_SCRIPT}

popd > /dev/null

# cleanup temp folder (only if empty)
rmdir $TEMP_DIR

