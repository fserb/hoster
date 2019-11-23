#!/bin/bash

echo "Hoster"

exec /usr/bin/supervisord -c ./supervisord.conf
