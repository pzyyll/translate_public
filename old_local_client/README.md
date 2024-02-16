# translate (已经失效，todo)

一个简单的翻译api（基于Google Cloud Translation API）,网上破解网页版的经常失效，自己便申请一个 api 用了

# 设置 google-api 权限

下载访问 api 权限文件 auth.json， 需要在 [google cloud console-IAM和管理-服务账号](https://console.cloud.google.com/iam-admin/serviceaccounts?project=root-cortex-366515&supportedpurview=project) 中下载

需要设置环境变量：

```bash
PROJECT_ID # 项目id
GOOGLE_APPLICATION_CREDENTIALS # 权限json
```

## linux:

```bash
export PROJECT_ID="root-cortex-366515"
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)"/auth_key/auth_key.json
```

## windows:

PowerShell:
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="auth_key/auth_key.json"
```

命令提示符
```bash
set GOOGLE_APPLICATION_CREDENTIALS="auth_key/auth_key.json"
```

## 以上环境变量，直接在 config.json 中设置就好了

```
{
    "google": {
        "project_id": "your_google_project_id",
        "auth_key": "your_google_auth_key_json_file_path"
    }
}

```

## 快速Build

- 先执行 install_deps.bat 安装依赖库
- 执行 build.bat 编译