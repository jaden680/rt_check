#!/bin/bash

rt_check_dir="rt_check"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

pushd "$SCRIPT_DIR" || exit

pwd
if [ ! -f "$rt_check_dir/.env" ]; then
    ./install.sh
fi
popd

ROOT_PATH=$(cd "$(dirname "$0")/$rt_check_dir" && pwd)
pushd "$ROOT_PATH" || exit
poetry run python -m main
popd