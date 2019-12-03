#!/bin/bash

set -e

cd "$(cd "$(dirname "$0")"; pwd -P)"

rm -rf tmp
mkdir -p tmp/repo

echo "Building docker image..."
docker build -q -t fserb/hoster.test ..

echo "Starting docker..."
docker rm -f hoster.test 2> /dev/null || true
docker run --detach --rm \
  --name hoster.test \
  -p 5666:5000 \
  -v $(pwd)/tmp/repo:/repo \
  -t fserb/hoster.test

echo "Waiting for docker to respond..."
until [ "$(curl -s http://localhost:5666/_fs/anything)" = "/anything: No such file or directory." ]; do
  sleep 0.1;
done

echo "Running tests..."
lib/bashtest.py tests/*

echo "Shutting down..."
docker rm -f hoster.test || true
