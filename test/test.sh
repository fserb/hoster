#!/bin/bash

set -e

cd "$(cd "$(dirname "$0")"; pwd -P)"

rm -rf tmp
mkdir -p tmp/repo tmp/www

echo "Building docker image..."
docker build --build-arg BUILD_ENV=dev -q -t fserb/hoster.dev ..

echo "Starting docker..."
docker rm -f hoster.test 2> /dev/null || true
docker run --rm \
  --name hoster.test \
  -p 5666:5000 \
  -v $(pwd)/tmp/www:/www \
  -v $(pwd)/tmp/repo:/repo \
  -t fserb/hoster.dev &

echo "Waiting for docker to respond..."
until [ "$(curl -s http://localhost:5666/_fs/anything)" = "/anything: No such file or directory." ]; do
  echo -n "."
  sleep 0.5;
done

echo
echo "Running tests..."
if ! lib/bashtest.py tests/*; then
  docker exec -it hoster.test cat /var/log/supervisor/server_stdout.log
  exit 1
fi

echo "Shutting down..."
docker rm -f hoster.test || true
