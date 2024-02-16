#!/bin/bash

TOOLS_DIR="$(readlink -f $(dirname $0))"
PROJECT_DIR="$(realpath $TOOLS_DIR/..)"
CLIENT_DIR="$PROJECT_DIR/ts_client"
DEPS_REQUIREMENTS_FILE="$TOOLS_DIR/client_requirements.txt"
# RES_DIR="$PROJECT_DIR/resources"
# COMMON_DIR="$PROJECT_DIR/ts_common"

echo "TOOLS_DIR: $TOOLS_DIR"
echo "PROJECT_DIR: $PROJECT_DIR"
# echo "CLIENT_DIR: $CLIENT_DIR"
# echo "DEPS_REQUIREMENTS_FILE: $DEPS_REQUIREMENTS_FILE"

init() {
    cd $CLIENT_DIR || exit

    python -m pip install --upgrade pip
    python -m pip install virtualenv --user
    python -m venv .venv --clear

    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r $DEPS_REQUIREMENTS_FILE

    cd - || exit
    cd $PROJECT_DIR || exit

    git submodule update --init --recursive

    echo $PROJECT_DIR/resources, $CLIENT_DIR/resources
    if [ ! -d $CLIENT_DIR/resources ] ; then
        ln -sf $PROJECT_DIR/resources $CLIENT_DIR/resources 
    fi

    if [ ! -d $CLIENT_DIR/ts_common ] ; then
        ln -sf $PROJECT_DIR/ts_common $CLIENT_DIR/ts_common
    fi

    cd - || exit
}

build() {
    cd $CLIENT_DIR || exit

    if [ ! -d .venv ] ; then
        init
    fi

    source .venv/bin/activate

    if [ ! -f ./ts_client.spec ] ; then 
        pyi-makespec --onefile --name ts_client translate_client.py
    fi

    pyinstaller --clean ./ts_client.spec

    cd - || exit
}

if [ "$1" == "init" ]; then
    init
elif [ "$1" == "build" ]; then
    build
else
    echo "Usage: $0 {init|build}"
    exit 1
fi
