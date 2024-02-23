## 使用 deploy.sh 部署服务器

- **确保当前环境已经安装 python3**

- 创建根目录并切换到该目录 ts_app:

    ```shell
    mkdir ts_app && cd ts_app
    ```

- 下载 deploy.sh: 
    ```shell
    wget https://raw.githubusercontent.com/pzyyll/translate_public/main/ts_server/tools/deploy.sh

    bash ./deploy.sh init

    bash ./deploy.sh service start
    # or sudo systemctl start ts_svr
    ```
    
## 一些需要自定义的配置选项：

默认配置路径在 `ts_app/ts_svr/ts_server/conf`
以及 Flask app 的配置文件 `ts_app/ts_svr/ts_server/config.py`

- 修改监听端口 `gunicorn_config.py`：
    ```
    bind = 127.0.0.1:8888

    ```

- 配置翻译api的配置 `ts_translate_api.conf`:
    ```
    {
        "google": {
            "project_id": "your_project_id",
            "auth_key": "path/to/your/google_auth_key.json",
            # "proxy":"socks5://127.0.0.1:1081"
        },
        "baidu": {
            "app_id": "your_app_id",
            "auth_key": "your_auth_key",
        }
    }
    ```

- Flask app 的环境配置 `ts_app/ts_svr/ts_server/config.py`：

    ```
    FLASK_ADMIN_SWATCH = "cerulean"
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/ts_sqlite.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '123456acbefg987123PPOOQWERTYUIOPASDFGHJKLZXCVBNM'
    RECAPTCHA_PUBLIC_KEY = "your_recaptcha_public_key"
    RECAPTCHA_PRIVATE_KEY = "your_recaptcha_private_key"
    SESSION_TYPE = 'filesystem'
    TESTING = True
    ```

## 使用 Nginx 作为Web前端

1. 安装 Nginx
2. 修改 Guni 的 ip 地址
    ``` shell
    bind = 127.0.0.1:6868
    # 本地转发建议使用 Unix 套接字
    # bind = unix:/path/to/your/ts_server.sock
    # nginx 对应的转发ip改成一致的 http://unix:/path/to/your/ts_server.sock
    ```
3. 运行部署脚本按照提示自动生成Nginx配置：`bash ./deploy.sh init-nginx-conf`