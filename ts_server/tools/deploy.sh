#!/bin/bash

SCRIPT_SOURCE_URL="https://raw.githubusercontent.com/pzyyll/translate_public/main/ts_server/tools/deploy.sh"
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
NGINX_CONFIG_TEMPLATE="$TOOLS_DIR/deploy_templates/ts_nginx.conf.template"

ENV_BIN_DIR="$WORK_DIR/.venv/bin"

DEFAULT_LOG_DIR="$WORK_DIR/logs"
DEFAULT_DATA_DIR="$WORK_DIR/data"
DEFAULT_FLASK_SESSION_DIR="$WORK_DIR/flask_session"
DEFAULT_CONFIG_DIR="$WORK_DIR/conf"

SERVICE_NAME="$(basename ${SERVICE_TEMPLATE%.template})"
NGINX_CONFIG_NAME="$(basename ${NGINX_CONFIG_TEMPLATE%.template})"

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
            echo -n "Do you want to remove it and re-initialize? [yes/no]: "
            read answer
            case $answer in
                [Yy][Ee][Ss])
                    echo "You chose to continue."
                    sudo rm -rf $PROJECT_DIR
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
    read -p "Bind ip and port (default: 127.0.0.1:6868): " bind || exit 1
    bind=${bind:-127.0.0.1:6868}
    sed -e "s|{{LOG_PATH}}|$DEFAULT_LOG_DIR|g" \
        -e "s|{{BIND}}|$bind|g" \
        $GUNICORN_CONFIG_TEMPLATE | tee $GUNI_CONFIG_FILE > /dev/null
}

init_flask_config() {
    cp $TS_TRANSLATE_CONFIG_TEMPLATE $TS_TRANSLATE_CONFIG_FILE
}


init_systemd_service() {
    if [ ! -d "/run/systemd/system" ]; then
        echo "Systemd not support!!!"
        exit 1
    fi

    GUNI_BIN="$ENV_BIN_DIR/gunicorn"

    sudo cp -f $SERVICE_TEMPLATE $SERVICE_FILE

    sudo sed -i "s|{{WORKING_DIR}}|$WORK_DIR|g" $SERVICE_FILE
    sudo sed -i "s|{{USER}}|$USER|g" $SERVICE_FILE
    sudo sed -i "s|{{GROUP}}|$GROUP|g" $SERVICE_FILE
    sudo sed -i "s|{{ENV_BIN_DIR}}|$ENV_BIN_DIR|g" $SERVICE_FILE
    sudo sed -i "s|{{GUNI_BIN}}|$GUNI_BIN|g" $SERVICE_FILE
    sudo sed -i "s|{{GUNI_CONFIG}}|$GUNI_CONFIG_FILE|g" $SERVICE_FILE

    # sudo sed \
    #     -e "s|{{WORKING_DIR}}|$WORK_DIR|g" \
    #     -e "s|{{USER}}|$USER|g" \
    #     -e "s|{{GROUP}}|$GROUP|g" \
    #     -e "s|{{ENV_BIN_DIR}}|$ENV_BIN_DIR|g" \
    #     -e "s|{{GUNI_BIN}}|$GUNI_BIN|g" \
    #     -e "s|{{GUNI_CONFIG}}|$GUNI_CONFIG_FILE/|g" \
    #     $SERVICE_TEMPLATE | sudo tee $SERVICE_FILE > /dev/null
}

uninstall_service() {
    if [ ! -d "/run/systemd/system" ]; then
        echo "Systemd not support!!!"
    fi
    sudo systemctl stop $SERVICE_NAME
    sudo systemctl disable $SERVICE_NAME
    sudo rm -f $SERVICE_FILE
    sudo systemctl daemon-reload
}

init_conf_not_service() {
    init_default_data_path
    init_gunicorn_config
    init_flask_config
}

# 定义更新函数
update_script() {
    echo "Updating script..."
    # 使用curl下载最新的脚本到当前目录的临时文件
    curl -H "Cache-Control: no-cache" -s $SCRIPT_SOURCE_URL -o "$0.tmp"
    
    # 检查下载是否成功
    if [ $? -eq 0 ]; then
        # 替换旧的脚本文件，并保留执行权限
        chmod --reference="$0" "$0.tmp"
        mv "$0.tmp" "$0"
        echo "The script has been updated."
    else
        echo "Failed to update the script."
        # 清理临时文件
        sudo rm -f "$0.tmp"
    fi
}


init_nginx_conf() {
    read -p "Nginx config path(default: /etc/nginx):" NGINX_CONFIG_DIR
    NGINX_CONFIG_DIR=${NGINX_CONFIG_DIR:-/etc/nginx}
    if [ ! -d "$NGINX_CONFIG_DIR" ]; then
        echo "Nginx not support!!!"
        exit 1
    fi
    if [ ! -f "$NGINX_CONFIG_DIR/nginx.conf" ]; then
        echo "Nginx not installed!!!"
        exit 1
    fi
    if [ -d "$NGINX_CONFIG_DIR/sites-available" ]; then
        NGINX_CONFIG_FILE="$NGINX_CONFIG_DIR/sites-available/$NGINX_CONFIG_NAME"
    elif [ -d "$NGINX_CONFIG_DIR/conf.d" ]; then
        NGINX_CONFIG_FILE="$NGINX_CONFIG_DIR/conf.d/$NGINX_CONFIG_NAME"
    else
        echo "Nginx config path not found!!!"
        exit 1
    fi

    read -p "Please enter the domain name or ip (default 127.0.0.1): " domain || exit 1
    domain=${domain:-127.0.0.1}
    read -p "Please enter the port (default 8888): " port || exit 1
    port=${port:-8888}
    read -p "Please enter the local web server ip and port (default http://127.0.0.1:6868): " flask_server || exit 1
    flask_server=${flask_server:-http://127.0.0.1:6868}

    echo "Copy config template $NGINX_CONFIG_TEMPLATE to $NGINX_CONFIG_FILE"
    sudo cp -f $NGINX_CONFIG_TEMPLATE $NGINX_CONFIG_FILE
    sudo sed -i "s|{{PUBLIC_IP}}|$domain|g" $NGINX_CONFIG_FILE
    sudo sed -i "s|{{PORT}}|$port|g" $NGINX_CONFIG_FILE
    sudo sed -i "s|{{FLASK_IP}}|$flask_server|g" $NGINX_CONFIG_FILE

    echo "Run 'sudo systemctl reload nginx' to apply changes."
    echo "Additional modifications are in the file: $NGINX_CONFIG_FILE"
}


up_source() {
    # 更新项目代码
    cd $PROJECT_DIR
    git pull origin main
    git read-tree -mu HEAD
    git submodule update --recursive
}

if [ "$1" == "init" ]; then
    init
    init_conf_not_service
    init_systemd_service

    echo "Default configuration file path: $DEFAULT_CONFIG_DIR"
    echo "Default log file path: $DEFAULT_LOG_DIR"
    echo "Default data file path: $DEFAULT_DATA_DIR"
    echo "Then run 'sudo systemctl start ts_svr' to start the service."
    exit 0
elif [ "$1" == "init-conf-noservice" ]; then
    if [ ! -d $PROJECT_DIR ]; then
        init
    fi
    init_conf_not_service

    echo "Default configuration file path: $DEFAULT_CONFIG_DIR"
    echo "Default log file path: $DEFAULT_LOG_DIR"
    echo "Default data file path: $DEFAULT_DATA_DIR"

    exit 0
elif [ "$1" == "install-service" ]; then
    init_systemd_service
    exit 0
elif [ "$1" == "uninstall-service" ]; then
    uninstall_service
    exit 0
elif [ "$1" == "service" ]; then
    if [ "$2" == "start" ]; then
        systemctl start $SERVICE_NAME
    elif [ "$2" == "stop" ]; then
        systemctl stop $SERVICE_NAME
    elif [ "$2" == "restart" ]; then
        systemctl restart $SERVICE_NAME
    elif [ "$2" == "status" ]; then
        systemctl status $SERVICE_NAME
    elif [ "$2" == "reload" ]; then
        systemctl daemon-reload
    else
        echo "Usage: $0 $1 {start|stop|restart|status|reload}"
        exit 1
    fi
elif [ "$1" == "up-source" ]; then
    up_source
elif [ "$1" == "init-pyenv" ]; then
    bash $TOOLS_DIR/svr_init.sh init
elif [ "$1" == "test-run" ]; then
    bash $TOOLS_DIR/svr_init.sh test_run
elif [ "$1" == "update" ]; then
    update_script
elif [ "$1" == "init-nginx-conf" ]; then
    init_nginx_conf
    exit 0
else
    echo "Usage: $0 {init|init-conf-noservice|install-service|uninstall-service|service|up-source|init-pyenv|test-run|update|init-nginx-conf}"
    exit 1
fi