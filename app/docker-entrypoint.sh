#!/bin/bash

set -ex

echo "Hoster"

mkdir -p /config/nginx/site-confs /var/lib/nginx /var/tmp/nginx /var/log/supervisor

[[ ! -f /config/nginx/nginx.conf ]] && \
  cp /app/defaults/nginx.conf /config/nginx/nginx.conf

[[ ! -f /config/nginx/site-confs/default ]] && \
  cp /app/defaults/default /config/nginx/site-confs/default

chown -R www:www /config /var/lib/nginx /var/tmp/nginx
chmod -R g+w /config/nginx

exec supervisord -c ./supervisord.conf
