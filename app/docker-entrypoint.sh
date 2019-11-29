#!/bin/bash

set -ex

echo "Hoster"

mkdir -p /data/db /data/configdb
chown -R mongodb:mongodb /data/db /data/configdb

mkdir -p /config/nginx/site-confs /var/lib/nginx /var/tmp/nginx

[[ ! -f /config/nginx/nginx.conf ]] && \
  cp /app/defaults/nginx.conf /config/nginx/nginx.conf

[[ ! -f /config/nginx/site-confs/default ]] && \
  cp /app/defaults/default /config/nginx/site-confs/default

mkdir -p /run/php

chown -R www:www \
  /config /var/lib/nginx /var/tmp/nginx /run/php
chmod -R g+w /config/nginx

sed -i "s#www-data.*#www#g" /etc/php/7.3/fpm/pool.d/www.conf

exec /usr/bin/supervisord -c ./supervisord.conf
