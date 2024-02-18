#!/bin/bash

TOOLS_DIR="$(readlink -f $(dirname $0))"
PROJECT_DIR="$(realpath $TOOLS_DIR/../..)"
SVR_DIR="$PROJECT_DIR/ts_server"
DEPS_REQUIREMENTS_FILE="$TOOLS_DIR/svr_requirements.txt"

# echo "TOOLS_DIR: $TOOLS_DIR"
# echo "SVR_DIR: $SVR_DIR"
# echo "DEPS_REQUIREMENTS_FILE: $DEPS_REQUIREMENTS_FILE"

init() {
    cd $SVR_DIR || exit

    python -m pip install --upgrade pip
    python -m pip install virtualenv --user
    python -m venv .venv --clear

    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r $DEPS_REQUIREMENTS_FILE

    cd - || exit
    cd $PROJECT_DIR || exit
    git submodule update --init --recursive

    if [ ! -d $SVR_DIR/ts_common ] ; then
        ln -sf $PROJECT_DIR/ts_common $SVR_DIR/ts_common
    fi

    cd - || exit
}

run() {
    cd $SVR_DIR || exit
    source .venv/bin/activate
    python -m flask run --debug
}

if [ "$1" == "init" ]; then
    init
elif [ "$1" == "run" ]; then
    run
else
    echo "Usage: $0 {init|run}"
    exit 1
fi

