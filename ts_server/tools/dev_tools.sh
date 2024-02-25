#!/bin/bash
# source deps
source /dev/stdin <<< "$(curl -s https://raw.githubusercontent.com/pzyyll/shell_snippets/main/color_echo.sh)"

# vars
TOOLS_DIR=${TOOLS_DIR:-"$(readlink -f $(dirname $0))"}
PROJECT_DIR="$(realpath $TOOLS_DIR/../..)"
WORK_DIR="$PROJECT_DIR/ts_server"
DEPS_REQUIREMENTS_FILE="$TOOLS_DIR/requirements.txt"

PYTHON_CMD=${PYTHON_CMD:-"python3"}

init() {
    echo "Initializing ts_server python running deps..."
    local original_dir=$(pwd)
    cd $WORK_DIR || exit 1

    echo "Start installing python venv ..."
    $PYTHON_CMD -m pip install --upgrade pip || exit 1
    $PYTHON_CMD -m pip install virtualenv --user
    $PYTHON_CMD -m venv .venv --clear

    echo "Start installing python deps ..."
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r $DEPS_REQUIREMENTS_FILE

    echo "Update pyhelper submodules ..."
    cd $PROJECT_DIR || exit
    git submodule update --init --recursive

    echo "Linking ts_common ..."
    if [ ! -d $WORK_DIR/ts_common ] ; then
        ln -sf $PROJECT_DIR/ts_common $WORK_DIR/ts_common
    fi

    cd $original_dir
}

run() {
    cd $WORK_DIR || exit
    source .venv/bin/activate
    python -m flask run --debug
}

case "$1" in
    init)
        init
        ;;
    run)
        run
        ;;
    *)
        echo "Usage: $0 {init|run}"
        exit 1
        ;;
esac

