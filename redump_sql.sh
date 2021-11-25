#!/bin/bash

set -euf -o pipefail
set -x

rm -f tmp.db
sqlite3 tmp.db <data.sql
sqlite3 tmp.db .dump >data.sql
rm -f tmp.db
