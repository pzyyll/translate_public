# translate
translate api

# 网络上的经常失效，自己申请一个 Clound API Key 来用吧，每个月 50 万字符免费，够用了

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

