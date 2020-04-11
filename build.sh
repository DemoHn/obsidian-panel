#!/bin/sh
OBS=obs
OBS_DEV=obs-dev
# build dev
rm -f ./$OBS ./$OBS_DEV

echo '=== build [obs] ==='
go build -o obs

echo '=== build [obs-dev] ==='
go build -o obs-dev ./cmd/obs-dev 