#!/bin/bash

set -e

rm -rf config/*

docker build -t fserb/hoster .

docker run --rm --name hoster \
  -p 5000:5000 \
  -v $(pwd)/www:/www \
  -v $(pwd)/repo:/repo \
  -v $(pwd)/data:/data \
  -v $(pwd)/config:/config \
  -t fserb/hoster
