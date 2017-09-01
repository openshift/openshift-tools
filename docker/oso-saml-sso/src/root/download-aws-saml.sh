#!/bin/sh
#
# Upstream:
#   https://signin.aws.amazon.com/static/saml-metadata.xml
#
# Tasks:
# - Download the certificate from Amazon's published URL
# - Extract X509 cert; from this get expire time, subject and cert data
# - Update the yaml file if the downloaded cert is newer and for the
#   same subject.
#
# Running:
# - Manually - run it when building the Docker image to avoid stale certs
#   in the image itself.  This is not automated since the updated yml 
#   should be committed to git.
# - Automatically - run when a pod starts up, and optionally during it's
#   life to avoid expiring cert
#
#
# Usage: $0 [ -f ] [ filename ]
# - "-f" (force) will create new file regardless if possible
# - filename defaults to ./aws_saml_cert.yml if not provided
#
#
# REVISION HISTORY
#   2017-08-09    Dave Baker    Script Created
#   2017-08-29    Dave Baker    Update - download/compare/patch
#


FORCE=0
if [ "$1" = "-f" ]; then
  FORCE=1
  shift
fi

# default
YML=./aws_saml_cert.yml
if [ ! -z "$1" ]; then
  YML=$1
fi

if [ ! -f $YML ]; then
  echo "No yaml config file found"
  if [ "$FORCE" = "1" ]; then
    echo "Force requested.  Continuing."
  else
    echo "Re-run with '-f' to force writing if desired."
    exit
  fi

  # set dummy expiry
  OLDEXP=0
else

  # Read info from prior cert
  OLDEXP=$( grep -Po '^aws_saml_expire: +\K[0-9]+' $YML )
  OLDSN=$(  grep -Po '^aws_saml_subject: +\K[a-zA-Z0-9=/.,: ]+' $YML )

  if [ -z "$OLDEXP" ]; then OLDEXP=0; fi

  # We expect a slowly rotating cert with a one year expiry.  If what
  # we already have expires more than 6 months out, then don't try to
  # update it.
  VAL=$( expr $OLDEXP - $( date +%s ) )
  if [ -z "$VAL" ]; then VAL=0; fi


  # 6 months is approx 60*60*24*30*6 = 15552000
  if [ "$VAL" -gt 15552000 ]; then
    echo "Existing cert is good for at least six months."
    if [ "$FORCE" = "1" ]; then
      echo "Force requested.  Continuing."
    else
      exit
    fi
  fi

fi


# Download from AWS and format as cert in temp file
NEWCERT=$( mktemp )

echo "Downloading https://signin.aws.amazon.com/static/saml-metadata.xml"

( 
  echo "-----BEGIN CERTIFICATE-----"

  wget -q -O - https://signin.aws.amazon.com/static/saml-metadata.xml | \
    sed -n '/<ds:X509Certificate>/,/<\/ds:X509Certificate>/p' | sed -e 's/\s*<\/*ds:X509Certificate>//'

  echo "-----END CERTIFICATE-----"

) > $NEWCERT



# Extra information from cert

# expires is epoch time for expiry of embedded cert
NOTAFTER=$( openssl x509 -noout -dates -in $NEWCERT | grep -Po 'notAfter=\K.*' )

if [ -z "$NOTAFTER" ]; then
  echo "No notAfter found in cert.  Skipping."
  exit
fi

# convert to date and validate - should be fully numeric
EXPIRES=$( date +%s -d "$NOTAFTER" )
VALIDATE=$( echo $EXPIRES | tr -cd 0-9 )
if [ "$EXPIRES" != "$VALIDATE" ]; then
  echo "validUntil did not convert to epoch time.  aborting."
  exit
fi

# subject used to ensure we don't switch with an unxpected, valid, but
# different cert
SUBJECT=$( openssl x509 -noout -subject -in $NEWCERT | grep -Po 'subject= *\K.*' )

if [ -z "$SUBJECT" ]; then
  echo "no subject= found in cert.  Skipping."
  exit
fi


# If we're not forcing, then test and abort if new cert isn't "good"
if [ "$FORCE" != "1" ]; then


  # Subject not match
  if [ "$OLDSN" != "$SUBJECT" ]; then
    echo "New cert is for a different SN.  Skipping."
    echo "Old: $OLDSN"
    echo "New: $SUBJECT"
    exit
  fi

  # Expiry must be newer
  if [ ! "$EXPIRES" -gt "$OLDEXP" ]; then
    echo "New cert does not expire later than existing cert.  Skipping."
    exit
  fi


fi



# Overwrite yml with new cert info

echo "Writing $YML"
(
  echo "# autogenerated on `date`"
  echo "# cert from https://signin.aws.amazon.com/static/saml-metadata.xml"
  echo "# expires on $NOTAFTER"
  echo "---"
  echo "aws_saml_subject: $SUBJECT"
  echo "aws_saml_expire: $EXPIRES"
  echo "aws_saml_x509: |"

  cat $NEWCERT | grep -v "^---" | sed -e 's/^/   /'

) > $YML


# Clean up temp file
rm -f $NEWCERT

