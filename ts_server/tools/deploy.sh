#!/bin/bash

PROJECT_REPOS="https://github.com/pzyyll/translate_public.git"
PROJECT_NAME="ts_svr"
CURRENT_DIR="$(pwd)"
WORK_DIR="$CURRENT_DIR/$PROJECT_NAME/ts_server"
PROJECT_DIR="$CURRENT_DIR/$PROJECT_NAME"
TOOLS_DIR="$PROJECT_DIR/ts_server/tools"
SERVICE_TEMPLATE="$TOOLS_DIR/deploy_templates/ts_svr.service.template"
GUNICORN_CONFIG_TEMPLATE="$TOOLS_DIR/deploy_templates/gunicorn_config.py.template"
TS_TRANSLATE_CONFIG_TEMPLATE="$TOOLS_DIR/deploy_templates/ts_translate_api.conf.template"
FLASK_CONFIG_FILE_TEMPLATE="$TOOLS_DIR/deploy_templates/config.py.template"
ENV_BIN_DIR="$WORK_DIR/.venv/bin"

DEFAULT_LOG_DIR="$WORK_DIR/logs"
DEFAULT_DATA_DIR="$WORK_DIR/data"
DEFAULT_FLASK_SESSION_DIR="$WORK_DIR/flask_session"
DEFAULT_CONFIG_DIR="$WORK_DIR/conf"

SERVICE_NAME=$(basename ${SERVICE_TEMPLATE%.template})

GUNI_CONFIG_FILE="$DEFAULT_CONFIG_DIR/$(basename ${GUNICORN_CONFIG_TEMPLATE%.template})"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
FLASK_CONFIG_FILE="$WORK_DIR/config.py"
TS_TRANSLATE_CONFIG_FILE="$DEFAULT_CONFIG_DIR/$(basename ${TS_TRANSLATE_CONFIG_TEMPLATE%.template})"

USER=$(whoami)
GROUP=$(id -g -n $USER)

init() {
    if [ -d $PROJECT_DIR ]; then
        while true; do
            echo "Project directory $PROJECT_DIR already exists. "
            echo "Do you want to remove it and re-initialize? [yes/no]"
            read answer
            case $answer in
                [Yy][Ee][Ss])
                    echo "You chose to continue."
                    rm -rf $PROJECT_DIR
                    break
                    ;;
                [Nn][Oo])
                    exit 0
                    ;;
                *)
                    echo "Invalid input. Please enter 'yes' or 'no'."
                    ;;
            esac
        done
    fi

    git clone --no-checkout $PROJECT_REPOS $PROJECT_NAME

    echo $PROJECT_DIR
    cd $PROJECT_DIR

    git sparse-checkout init

    git sparse-checkout set ts_server/ ts_common/ .gitmodules

    git pull origin main
    git read-tree -mu HEAD

    # 更新依赖的子模块
    git submodule init
    # 替换掉 ssh 成 https
    git submodule set-url ts_common/external_libs/pyhelper https://github.com/pzyyll/python_common.git
    git submodule update --recursive

    bash $TOOLS_DIR/svr_init.sh init

    cp $FLASK_CONFIG_FILE_TEMPLATE $FLASK_CONFIG_FILE
}

init_default_data_path() {
    mkdir -p $DEFAULT_LOG_DIR
    mkdir -p $DEFAULT_DATA_DIR
    mkdir -p $DEFAULT_FLASK_SESSION_DIR
    mkdir -p $DEFAULT_CONFIG_DIR
}

init_gunicorn_config() {
    sed -e "s|{{LOG_PATH}}|$DEFAULT_LOG_DIR|g" \
        $GUNICORN_CONFIG_TEMPLATE > $GUNI_CONFIG_FILE
}

init_systemd_service() {
    if [ ! -d "/run/systemd/system" ]; then
        echo "Systemd not support!!!"
        exit 1
    fi
    template_file_name=$(basename $SERVICE_TEMPLATE)
    service_file_name="${template_file_name%.template}"
    GUNI_BIN="$ENV_BIN_DIR/gunicorn"

    sed -e "s|{{WORKING_DIR}}|$WORK_DIR|g" \
        -e "s|{{USER}}|$USER|g" \
        -e "s|{{GROUP}}|$GROUP|g" \
        -e "s|{{ENV_BIN_DIR}}|$ENV_BIN_DIR|g" \
        -e "s|{{GUNI_BIN}}|$GUNI_BIN|g" \
        -e "s|{{GUNI_CONFIG}}|$GUNI_CONFIG_FILE/|g" \
        $SERVICE_TEMPLATE > $SERVICE_FILE
}

init_config() {
    cp $TS_TRANSLATE_CONFIG_TEMPLATE $TS_TRANSLATE_CONFIG_FILE
}

uninstall_service() {
    if [ ! -d "/run/systemd/system" ]; then
        echo "Systemd not support!!!"
    fi
    systemctl stop $SERVICE_NAME
    systemctl disable $SERVICE_NAME
    rm -f $SERVICE_FILE
    systemctl daemon-reload
}

init_conf_not_service() {
    init_default_data_path
    init_gunicorn_config
    init_config
}

if [ $1 == "init" ]; then
    init
    init_conf_not_service
    init_systemd_service
    echo "Init success!"
    echo "Default configuration file path: $DEFAULT_CONFIG_DIR"
    echo "Default log file path: $DEFAULT_LOG_DIR"
    echo "Default data file path: $DEFAULT_DATA_DIR"
    echo "Then run 'sudo systemctl start ts_svr' to start the service."
    exit 0
elif [ $1 == "init_conf" ]; then
    if [ ! -d $PROJECT_DIR ]; then
        init
    fi
    init_conf_not_service
    exit 0
elif [ $1 == "uninstall_service" ]; then
    uninstall_service
    exit 0
elif [ $1 == "service" ]; then
    if [ $2 == "start" ]; then
        systemctl start $SERVICE_NAME
    elif [ $2 == "stop" ]; then
        systemctl stop $SERVICE_NAME
    elif [ $2 == "restart" ]; then
        systemctl restart $SERVICE_NAME
    elif [ $2 == "status" ]; then
        systemctl status $SERVICE_NAME
    elif [ $2 == "reload" ]; then
        systemctl daemon-reload
    else
        echo "Usage: $0 $1 {start|stop|restart|status|reload}"
        exit 1
    fi
elif [ $1 == "test_init" ]; then
    bash $TOOLS_DIR/svr_init.sh test_init
elif [ $1 == "test_run" ]; then
    bash $TOOLS_DIR/svr_init.sh test_run
else
    echo "Usage: $0 {init}"
    exit 1
fi