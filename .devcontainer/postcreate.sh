#!/bin/bash

set -euf -o pipefail
set -x

pip3 install --upgrade pip
pip3 install isort pytest
pip3 install -r requirements.txt

git submodule init
git submodule update
