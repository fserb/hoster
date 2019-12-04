#!/bin/bash

cat <<EOF

  _               _
 | |             | |
 | |__   ___  ___| |_ ___ _ __
 | '_ \ / _ \/ __| __/ _ \ '__|
 | | | | (_) \__ \ ||  __/ |
 |_| |_|\___/|___/\__\___|_|

EOF

set -ex

groupadd -r www && useradd -r -g www www

mkdir -p /config/nginx/site-confs /var/lib/nginx /var/tmp/nginx /var/log/supervisor

[[ ! -f /config/nginx/nginx.conf ]] && \
  cp /app/defaults/nginx.conf /config/nginx/nginx.conf

[[ ! -f /config/nginx/site-confs/default ]] && \
  cp /app/defaults/default /config/nginx/site-confs/default

chown -R www:www /config /var/lib/nginx /var/tmp/nginx /run/lock
chmod -R g+w /config/nginx
rm -rf /run/lock/fcgiwrap.sock

PYTHONUNBUFFERED=1 exec supervisord -c ./supervisord.conf
