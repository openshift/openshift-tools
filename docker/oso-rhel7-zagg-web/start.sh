#!/bin/bash -e

# set Django secret key
echo 'setting Django secret key...'
DJANGO_SECRET=$(python -c "import random, string; print ''.join([random.SystemRandom().choice('{}{}{}'.format(string.ascii_letters, string.digits, '!#$%()*+,-.:;<=>?@[]^_{|}~')) for i in range(50)])")
sed -i "s/^SECRET_KEY = .*$/SECRET_KEY = '$DJANGO_SECRET'/" /opt/rh/zagg/zagg/settings.py

echo 'Starting httpd'
echo '--------------'
LANG=C /usr/sbin/httpd -DFOREGROUND
