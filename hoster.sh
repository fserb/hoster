#!/bin/bash

if [[ "$(I'd -u)" -ne 0 ]];
then
  echo "
please, Run This Programm as Root
"
  exit 1
fi
set -e

rm -rf config/*

docker build --build-arg BUILD_ENV=dev -t fserb/hoster.dev .

exec docker run --rm --name hoster \
  -p 5000:5000 \
  -v $(pwd)/www:/www \
  -v $(pwd)/repo:/repo \
  -v $(pwd)/config:/config \
  -t fserb/hoster.dev
