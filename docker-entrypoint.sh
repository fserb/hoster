#!/bin/bash

set -e

echo "Hoster"

mkdir -p /data/db /data/configdb
chown -R mongodb:mongodb /data/db /data/configdb

exec /usr/bin/supervisord -c ./supervisord.conf
