#!/bin/bash

set -euf -o pipefail
set -x

git submodule init
git submodule update

pushd data/
git checkout data
git pull --ff

rm -f data.db
sqlite3 data.db <data.sql
