#!/bin/bash

set -e

rm -rf .config/

docker build -t fserb/hoster hoster

docker run --rm --name hoster \
  -p 5000:5000 \
  -v $(pwd):/www \
  -v $(pwd)/.repo:/repo \
  -v $(pwd)/.config:/config \
  -t fserb/hoster
