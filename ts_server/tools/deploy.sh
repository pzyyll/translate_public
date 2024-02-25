#!/bin/bash
# source deps
source /dev/stdin <<< "$(curl -s https://raw.githubusercontent.com/pzyyll/shell-snippets/main/load.sh | bash -s -- color_echo mk_dir)"


USER=$(whoami)
GROUP=$(id -g -n $USER)
SCRIPT_SOURCE_URL="https://raw.githubusercontent.com/pzyyll/translate_public/main/ts_server/tools/deploy.sh"
PROJECT_REPOS="https://github.com/pzyyll/translate_public.git"
PROJECT_NAME="ts_svr"
CURRENT_DIR="$(pwd)"
TS_ENV_FILE="~/.ts_env"
PYTHON_CMD="python"

TEMP_DIR=$(mktemp -d)
TEMP_MK_FILE_LOG="$TEMP_DIR/mk_files.log"


exit_status() {
    EXIT_STATUS="$1"
    exit $EXIT_STATUS
}


local_mkdir() {
    # log the first not exist dir
    local dir="$1"
    if [ ! -d "$dir" ]; then
        local result=$(USER=$USER mk_dir "$dir")
        if [ "$?" -eq 0 ]; then
            echo "$result" >> "$TEMP_MK_FILE_LOG"
            return 0
        else
            echo "Error: Failed to create directory '$dir'."
            return 1
        fi
    fi
}


check_python_version() {
    local python_cmd="$1"

    if [ -z "$python_cmd" ]; then
        if command -v python3 &>/dev/null; then
            python_cmd=python3
        elif command -v python &>/dev/null; then
            python_cmd=python
        else
            echo "Python is not installed. Please install Python 3."
            return 1
        fi
    elif [ ! -x "$python_cmd" ]; then
        echo "The provided Python path '$python_cmd' is not an executable."
        return 1
    fi

    # 检查 Python 可执行文件
    if ! $python_cmd -c '' &>/dev/null; then
        echo "The provided Python path '$python_cmd' is not valid"
        return 1
    fi

    # 检查 Python 版本
    local python_version=$($python_cmd -c 'import sys; print(sys.version_info.major)')
    if [ "$python_version" -lt 3 ]; then
        echo "Found Python, but it is not Python 3. Detected version: Python $python_version"
        return 1
    else
        PYTHON_CMD=$python_cmd
        echo "Detected Python 3 version: $($python_cmd --version)"
        return 0
    fi
}


get_python_env() {
    local python_version=$(check_python_version "${1}")
    result=$?
    if [ ! "$result" -eq 0 ]; then
        echo "未检测到可用的 Python 版本, 请安装 Python 3.6或更高版本。如果你已经安装，可以提供其安装路径给我。"
        while true; do
            read -p "输入：/path/to/your/bin/python3，或者回车退出：" PYTHON_CMD
            if [ -z "$PYTHON_CMD" ]; then
                color_echo "See you next time! :)" green
                exit_status 1
            fi
            python_version=$(check_python_version "$PYTHON_CMD")
            if [ "$?" -eq 0 ]; then
                break
            else
                echo "提供的 Python 路径未检测到，请重新输入..."
            fi
        done    
    fi
    color_echo "$python_version" yellow
}


check_git() {
    # 检查 Git 是否已安装
    if ! command -v git &> /dev/null
    then
        echo "Git 未安装。正在尝试安装 Git..."
        read -p "Git 未安装，是否尝试安装？$(color_echo "[yes/no]" yellow italic): " answ
        case $answ in
            [Yy][Ee][Ss])
                color_echo "开始安装 Git..." yellow
                ;;
            *)
                color_echo "See you next time! :)" green
                exit_status 1
                ;;
        esac
        # 检测操作系统
        OS="$(uname -s)"
        case "${OS}" in
            Linux*)     os=Linux;;
            Darwin*)    os=Mac;;
            # CYGWIN*)    os=Cygwin;;
            # MINGW*)     os=MinGw;;
            *)          os="UNKNOWN:${OS}"
        esac

        echo "检测到的操作系统：${os}"

        # 根据操作系统安装 Git
        case "${os}" in
            Linux)
                if [ -f /etc/debian_version ]; then
                    # 基于 Debian 的系统
                    sudo apt-get update
                    sudo apt-get install git -y
                elif [ -f /etc/redhat-release ]; then
                    # 基于 RedHat 的系统
                    sudo yum update
                    sudo yum install git -y
                else
                    color_echo "未检测到当前系统可用安装包, 请手动安装 Git: https://git-scm.com/downloads" red

                fi
                ;;
            Mac)
                # 使用 Homebrew 安装 Git
                which -s brew
                if [[ $? != 0 ]] ; then
                    # 安装 Homebrew
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                fi
                brew install git
                ;;
            *)
                color_echo "未检测到当前系统可用安装包, 请手动安装 Git: https://git-scm.com/downloads" red
                ;;
        esac
    else
        color_echo "Git 版本：$(git --version)" yellow
    fi
}


initialize_variables() {
    if [ ! "${PROJECT_DIR:-}" ]; then
        PROJECT_DIR="$CURRENT_DIR/$PROJECT_NAME"
    fi

    WORK_DIR="$PROJECT_DIR/ts_server"
    TOOLS_DIR="$PROJECT_DIR/ts_server/tools"
    PYENV_DEPS_REQUIREMENTS_FILE="$TOOLS_DIR/requirements.txt"
    SERVICE_TEMPLATE="$TOOLS_DIR/deploy_templates/ts_svr.service.template"
    GUNICORN_CONFIG_TEMPLATE="$TOOLS_DIR/deploy_templates/gunicorn_config.py.template"
    TS_TRANSLATE_CONFIG_TEMPLATE="$TOOLS_DIR/deploy_templates/ts_translate_api.conf.template"
    FLASK_CONFIG_FILE_TEMPLATE="$TOOLS_DIR/deploy_templates/config.py.template"
    NGINX_CONFIG_TEMPLATE="$TOOLS_DIR/deploy_templates/ts_nginx.conf.template"

    ENV_BIN_DIR="$WORK_DIR/.venv/bin"

    APP_DATA="$WORK_DIR/app_data"
    DEFAULT_LOG_DIR="$APP_DATA/logs"
    DEFAULT_DATA_DIR="$APP_DATA/db"
    DEFAULT_FLASK_SESSION_DIR="$APP_DATA/flask_session"
    DEFAULT_CONFIG_DIR="$APP_DATA/conf"

    SERVICE_NAME="$(basename ${SERVICE_TEMPLATE%.template})"
    NGINX_CONFIG_NAME="$(basename ${NGINX_CONFIG_TEMPLATE%.template})"

    GUNI_CONFIG_FILE="$DEFAULT_CONFIG_DIR/$(basename ${GUNICORN_CONFIG_TEMPLATE%.template})"
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
    FLASK_CONFIG_FILE="$WORK_DIR/config.py"
    TS_TRANSLATE_CONFIG_FILE="$DEFAULT_CONFIG_DIR/$(basename ${TS_TRANSLATE_CONFIG_TEMPLATE%.template})"
}


check_ip_port() {
    # 输入参数：形如“127.0.0.1:8080”的字符串
    local input="$1"

    # IPv4地址和端口的正则表达式
    local regex="^([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}$"

    # 检查输入是否符合正则表达式
    if [[ $input =~ $regex ]]; then
        ip="${input%:*}" # 提取IP部分
        port="${input##*:}" # 提取端口部分
        
        # 分割IP地址，检查每部分是否小于等于255
        IFS='.' read -r -a ip_parts <<< "$ip"
        valid_ip=true
        for part in "${ip_parts[@]}"; do
            if ((part > 255)); then
                valid_ip=false
                break
            fi
        done
        
        # 检查端口号是否在0到65535之间
        valid_port=false
        if ((port >= 0 && port <= 65535)); then
            valid_port=true
        fi
        
        if $valid_ip && $valid_port; then
            echo "Valid input: IP address and port are correct."
            return 0
        else
            color_echo "Invalid input: IP address(0~255) or port(0~65535) is incorrect." red
            return 1
        fi
    else
        color_echo "Invalid input format. Please use the format 'IP:Port'." red
        return 1
    fi
}


init() {
    read -p "Set the root path of the app service(default: $(color_echo "${CURRENT_DIR}" green underline)) :" project_root_path
    PROJECT_ROOT_DIR="${project_root_path:-$CURRENT_DIR}"

    if [ ! -d $PROJECT_ROOT_DIR ]; then
        read -p "The path does not exist. Do you want to create?$(color_echo "[yes/no]" yellow italic): " answ
        case $answ in
            [Yy][Ee][Ss])
                local_mkdir $PROJECT_ROOT_DIR || exit_status 1
                # 更新成绝对路径，以防输入的是个相对路径
                # (Update to absolute path in case the input is a relative path)
                break
                ;;
            *)
                color_echo "See you next time! :)" green
                exit_status 1
                ;;
        esac
    fi

    PROJECT_ROOT_DIR=$(realpath "$PROJECT_ROOT_DIR")
    PROJECT_DIR="$PROJECT_ROOT_DIR/$PROJECT_NAME"
    if [ -d $PROJECT_DIR ]; then
        while true; do
            echo "Project directory $(color_echo $PROJECT_DIR green underline) already exists. "
            read -p "Do you want to $(color_echo "remove" red) it and re-initialize? $(color_echo "[yes/no]" yellow italic): " answer
            case $answer in
                [Yy][Ee][Ss])
                    echo "Remove old files...."
                    sudo rm -rf $PROJECT_DIR
                    break
                    ;;
                [Nn][Oo])
                    exit_status 0
                    ;;
                *)
                    echo "Invalid input. Enter '$(color_echo "yes" red)' or '$(color_echo "no" red)'."
                    ;;
            esac
        done
    fi

    # 重新根据 PROJECT_DIR 路径初始化相关路径
    initialize_variables
    echo "项目将会在以下路径创建：$(color_echo "$PROJECT_DIR" green)"

    git clone --no-checkout $PROJECT_REPOS $PROJECT_DIR || exit_status 1
    echo "$PROJECT_DIR" >> "$TEMP_MK_FILE_LOG"

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
    local_mkdir $DEFAULT_LOG_DIR
    local_mkdir $DEFAULT_DATA_DIR
    local_mkdir $DEFAULT_FLASK_SESSION_DIR
    local_mkdir $DEFAULT_CONFIG_DIR
}


init_gunicorn_config() {
    if [ -f $GUNI_CONFIG_FILE ]; then
        while true; do
            read -p "Gunicorn config file $(color_echo "$GUNI_CONFIG_FILE" green) already exists. Do you want to overwrite it? $(color_echo "[yes/no]" yellow italic): " answer
            case $answer in
                [Yy][Ee][Ss])
                    break
                    ;;
                [Nn][Oo])
                    return 1
                    ;;
                *)
                    echo "Invalid input. Enter '$(color_echo "yes" red)' or '$(color_echo "no" red)'."
                    ;;
            esac
        done
    fi

    while true; do
        read -p "Bind ip and port (default: $(color_echo "127.0.0.1:6868" green)): " bind
        bind=${bind:-127.0.0.1:6868}
        result_info=$(check_ip_port $bind)
        if [ $? -eq 0 ]; then
            break
        else
            echo $result_info
        fi
    done

    sed -e "s|{{LOG_PATH}}|$DEFAULT_LOG_DIR|g" \
        -e "s|{{BIND}}|$bind|g" \
        $GUNICORN_CONFIG_TEMPLATE | tee $GUNI_CONFIG_FILE > /dev/null
}


init_flask_config() {
    cp $TS_TRANSLATE_CONFIG_TEMPLATE $TS_TRANSLATE_CONFIG_FILE
}


init_systemd_service() {
    if [ ! -d "/run/systemd/system" ]; then
        color_echo "Systemd not support." red
        return 1
    fi

    GUNI_BIN="$ENV_BIN_DIR/gunicorn"

    sudo cp -f $SERVICE_TEMPLATE $SERVICE_FILE

    sudo sed -i "s|{{WORKING_DIR}}|$WORK_DIR|g" $SERVICE_FILE
    sudo sed -i "s|{{USER}}|$USER|g" $SERVICE_FILE
    sudo sed -i "s|{{GROUP}}|$GROUP|g" $SERVICE_FILE
    sudo sed -i "s|{{ENV_BIN_DIR}}|$ENV_BIN_DIR|g" $SERVICE_FILE
    sudo sed -i "s|{{GUNI_BIN}}|$GUNI_BIN|g" $SERVICE_FILE
    sudo sed -i "s|{{GUNI_CONFIG}}|$GUNI_CONFIG_FILE|g" $SERVICE_FILE
}


uninstall_service() {
    if [ ! -d "/run/systemd/system" ]; then
        color_echo "Systemd not support!!!" red
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
        color_echo "Failed to update the script." red
        # 清理临时文件
        sudo rm -f "$0.tmp"
    fi
}


init_nginx_conf() {
    read -p "Nginx config path(default: $(color_echo "/etc/nginx" green)):" NGINX_CONFIG_DIR
    NGINX_CONFIG_DIR=${NGINX_CONFIG_DIR:-/etc/nginx}
    if [ ! -d "$NGINX_CONFIG_DIR" ]; then
        color_echo "Nginx not support!!!" red
        exit_status 1
    fi
    if [ ! -f "$NGINX_CONFIG_DIR/nginx.conf" ]; then
        color_echo "Nginx not installed!!!" red
        exit_status 1
    fi
    if [ -d "$NGINX_CONFIG_DIR/sites-available" ]; then
        NGINX_CONFIG_FILE="$NGINX_CONFIG_DIR/sites-available/$NGINX_CONFIG_NAME"
    elif [ -d "$NGINX_CONFIG_DIR/conf.d" ]; then
        NGINX_CONFIG_FILE="$NGINX_CONFIG_DIR/conf.d/$NGINX_CONFIG_NAME"
    else
        color_echo "Nginx config path not found!!!" red
        exit_status 1
    fi

    read -p "Enter the domain name or ip (default $(color_echo "127.0.0.1" green underline)): " domain
    domain=${domain:-127.0.0.1}
    read -p "Enter the port (default $(color_echo "8888" green underline)): " port
    port=${port:-8888}
    read -p "Enter the local web server ip and port (default $(color_echo "http://127.0.0.1:6868" green underline)): " flask_server
    flask_server=${flask_server:-http://127.0.0.1:6868}

    echo "Copy config template $NGINX_CONFIG_TEMPLATE to $(color_echo "$NGINX_CONFIG_FILE" green) ..."
    sudo cp -f $NGINX_CONFIG_TEMPLATE $NGINX_CONFIG_FILE
    sudo sed -i "s|{{PUBLIC_IP}}|$domain|g" $NGINX_CONFIG_FILE
    sudo sed -i "s|{{PORT}}|$port|g" $NGINX_CONFIG_FILE
    sudo sed -i "s|{{FLASK_IP}}|$flask_server|g" $NGINX_CONFIG_FILE

    echo "Run $(color_echo "'sudo systemctl reload nginx'" red) to apply changes."
    echo "Additional modifications are in the file: $(color_echo "$NGINX_CONFIG_FILE" green)"
}


up_source() {
    # 更新项目代码
    color_echo "Updating project source code..." yellow
    cd $PROJECT_DIR
    git pull origin main
    if [ $1 == "force" ]; then
        git read-tree -mu HEAD
    fi
    git submodule update --init --recursive
}


init_pyenv() {
    color_echo "\nInitializing python running deps..." yellow

    cd $WORK_DIR || exit_status 1

    color_echo "\nStart installing python venv ..." yellow
    $PYTHON_CMD -m pip install --upgrade pip || exit_status 1
    $PYTHON_CMD -m pip install virtualenv --user
    $PYTHON_CMD -m venv .venv --clear

    color_echo "Start installing python deps ..." yellow
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r $DEPS_REQUIREMENTS_FILE

    color_echo "Linking ts_common ..." yellow
    if [ ! -d $WORK_DIR/ts_common ] ; then
        ln -sf $PROJECT_DIR/ts_common $WORK_DIR/ts_common
    fi
}

service() {
    if [ "$1" == "start" ]; then
        systemctl start $SERVICE_NAME
    elif [ "$1" == "stop" ]; then
        systemctl stop $SERVICE_NAME
    elif [ "$1" == "restart" ]; then
        systemctl restart $SERVICE_NAME
    elif [ "$1" == "status" ]; then
        systemctl status $SERVICE_NAME
    elif [ "$1" == "reload" ]; then
        systemctl daemon-reload
    else
        echo "Usage: $0 $1 {start|stop|restart|status|reload}"
    fi
}


help() {
    echo "Usage: $0 {init|init-conf-noservice|install-service|uninstall-service|service|up-source|init-pyenv|test-run|update|init-nginx-conf}"
    echo "init: Initialize the project and install the service."
    echo "init-conf-noservice: Initialize the project without installing the service."
    echo "install-service: Install the service."
    echo "uninstall-service: Uninstall the service."
    echo "service: Start, stop, restart, status, or reload the service."
    echo "up-source: Update the project source code."
    echo "init-pyenv: Initialize the python environment."
    echo "test-run: Run the project in debug mode."
    echo "update: Update the script."
    echo "init-nginx-conf: Initialize the nginx configuration."
}


exit_cleanup() {
    # 只在 EXIT_STATUS 非零且 TEMP_MK_FILE_LOG 文件存在时执行清理
    if [[ $EXIT_STATUS -ne 0 ]] && [[ -f $TEMP_MK_FILE_LOG ]]; then
        # 读取 TEMP_MK_FILE_LOG 文件中的每个条目并删除
        cat $TEMP_MK_FILE_LOG
        xargs -I {} sudo rm -rf {} < $TEMP_MK_FILE_LOG
    fi
    rm -rf "$TEMP_DIR"
}


sig_cleanup() {
    exit_status 1
}


trap exit_cleanup EXIT
trap sig_cleanup SIGINT SIGTERM


if [ -f $TS_ENV_FILE ]; then
    source $TS_ENV_FILE
fi

check_git
get_python_env
initialize_variables


case $1 in
    "init")
        init
        init_conf_not_service
        init_systemd_service

        color_echo "Default configuration file path: $(color_echo "$DEFAULT_CONFIG_DIR" green)"
        color_echo "Default log file path: $(color_echo "$DEFAULT_LOG_DIR" green)"
        color_echo "Default data file path: $(color_echo "$DEFAULT_DATA_DIR" green)"
        color_echo "Then run $(color_echo "'sudo systemctl start ts_svr'" red) to start the service."
        ;;
    "install-service")
        init_systemd_service
        ;;
    "uninstall-service")
        uninstall_service
        ;;
    "service")
        service $2
        ;;
    "up-source")
        up_source force
        ;;
    "init-pyenv")
        up_source
        init_pyenv
        ;;
    "update")
        update_script
        ;;
    "init-nginx-conf")
        init_nginx_conf
        ;;
    *)
        help
        ;;
esac
