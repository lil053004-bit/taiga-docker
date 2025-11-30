# Taiga 生产环境部署指南（宝塔面板 + 顶级域名）

本指南将帮助您在使用宝塔面板的服务器上部署 Taiga 项目管理系统。

## 前置要求

- 已安装宝塔面板（7.7.0 或更高版本）
- 已通过宝塔安装 Docker 和 Docker Compose
- 已安装 Nginx（1.20 或更高版本）
- 顶级域名已配置 DNS 解析指向服务器
- 服务器配置建议：2核CPU、4GB内存、40GB磁盘

## 第一步：修改环境变量配置

在部署前，您必须修改 `.env` 文件中的以下配置：

### 必须修改的配置项

1. **域名配置**
```bash
TAIGA_DOMAIN=yourdomain.com  # 改为您的实际域名（不带 http:// 和端口号）
```

2. **安全密钥配置**（生成 50 位以上的随机字符串）
```bash
SECRET_KEY="your-random-50-character-secret-key-here"
```

3. **数据库密码**（使用强密码）
```bash
POSTGRES_PASSWORD=your-strong-database-password-here
```

4. **RabbitMQ 配置**（使用强密码）
```bash
RABBITMQ_PASS=your-strong-rabbitmq-password-here
RABBITMQ_ERLANG_COOKIE=your-unique-erlang-cookie-random-value
```

### 生成随机密钥的方法

在终端中执行以下命令生成随机字符串：

```bash
# 生成 SECRET_KEY（50 字符）
openssl rand -base64 50

# 生成 POSTGRES_PASSWORD（32 字符）
openssl rand -base64 32

# 生成 RABBITMQ_PASS（32 字符）
openssl rand -base64 32

# 生成 RABBITMQ_ERLANG_COOKIE（32 字符）
openssl rand -base64 32
```

## 第二步：上传项目文件到服务器

1. 将整个项目文件夹上传到服务器（推荐路径：`/www/wwwroot/taiga`）
2. 确保以下文件和目录完整：
   - `.env`（已修改配置）
   - `docker-compose.yml`
   - `docker-compose-inits.yml`
   - `launch-taiga.sh`
   - `taiga-manage.sh`
   - `taiga-gateway/taiga.conf`

3. 设置文件权限：
```bash
cd /www/wwwroot/taiga
chmod 755 launch-taiga.sh taiga-manage.sh
```

## 第三步：启动 Docker 容器

1. 在宝塔面板打开终端，进入项目目录：
```bash
cd /www/wwwroot/taiga
```

2. 执行启动脚本：
```bash
bash launch-taiga.sh
```

3. 等待 3-5 分钟让所有服务启动完成

4. 验证容器运行状态：
```bash
docker ps
```

您应该看到 7 个正在运行的容器：
- taiga-db
- taiga-back
- taiga-async
- taiga-async-rabbitmq
- taiga-front
- taiga-events
- taiga-events-rabbitmq
- taiga-protected
- taiga-gateway

## 第四步：创建 Taiga 管理员账户

1. 在项目目录执行管理脚本：
```bash
bash taiga-manage.sh createsuperuser
```

2. 按照提示输入：
   - 用户名（Username）
   - 邮箱地址（Email address）
   - 密码（Password，输入两次确认）

3. 记录管理员登录凭据到安全位置

## 第五步：在宝塔面板配置网站

1. 登录宝塔面板，点击左侧菜单"网站"

2. 点击"添加站点"按钮

3. 填写网站信息：
   - **域名**：填写您的域名（例如：`yourdomain.com`）
   - 可以同时添加 www 子域名（例如：`www.yourdomain.com`）
   - **根目录**：可以随意设置（因为使用反向代理）
   - **PHP 版本**：选择"纯静态"

4. 点击"提交"创建网站

## 第六步：申请和配置 SSL 证书

1. 在网站列表中，找到刚创建的网站，点击"设置"

2. 点击左侧"SSL"选项卡

3. 选择"Let's Encrypt"标签页

4. 勾选您的域名和 www 域名

5. 填写邮箱地址（用于证书到期提醒）

6. 点击"申请"按钮

7. 等待证书申请成功

8. 开启"强制 HTTPS"选项

## 第七步：配置反向代理

### 方法一：使用宝塔反向代理功能

1. 在网站设置页面，点击左侧"反向代理"

2. 点击"添加反向代理"

3. 填写配置：
   - **代理名称**：Taiga
   - **目标 URL**：`http://127.0.0.1:9090`
   - **发送域名**：保持开启

4. 点击"提交"

### 方法二：手动编辑 Nginx 配置（推荐，功能更完整）

1. 在网站设置页面，点击左侧"配置文件"

2. 找到 `server` 块，在 `location` 配置之前添加以下内容：

```nginx
# 客户端上传文件大小限制
client_max_body_size 100M;

# Taiga 主应用反向代理
location / {
    proxy_pass http://127.0.0.1:9090;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Scheme $scheme;
    proxy_redirect off;

    # WebSocket 支持
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}

# WebSocket 事件连接（特殊配置）
location /events {
    proxy_pass http://127.0.0.1:9090/events;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # WebSocket 超时设置（7 天）
    proxy_connect_timeout 7d;
    proxy_send_timeout 7d;
    proxy_read_timeout 7d;
}
```

3. 点击"保存"

4. 重载 Nginx 配置

## 第八步：验证部署成功

### 1. 访问网站
在浏览器中访问：`https://yourdomain.com`

您应该看到 Taiga 登录页面

### 2. 登录系统
使用第四步创建的管理员账户登录

### 3. 测试功能
- 创建一个测试项目
- 上传文件测试文件上传功能
- 查看浏览器开发者工具（F12），切换到"网络"（Network）标签
- 验证 WebSocket 连接：
  - 过滤 WS 连接
  - 应该看到 `wss://yourdomain.com/events` 连接状态为 101（协议切换成功）

### 4. 检查容器状态
```bash
docker ps -a
```

所有容器的 STATUS 应该显示"Up"（运行中）

## 第九步：备份配置（重要！）

为了数据安全，请定期备份以下内容：

### 1. 在宝塔面板设置计划任务

1. 点击左侧菜单"计划任务"
2. 添加备份任务：
   - **任务类型**：备份目录
   - **执行周期**：每天
   - **备份目录**：`/www/wwwroot/taiga`

### 2. 备份 Docker 数据卷

```bash
# 创建备份目录
mkdir -p /www/backup/taiga

# 备份数据库数据卷
docker run --rm -v taiga-db-data:/data -v /www/backup/taiga:/backup alpine tar czf /backup/taiga-db-data.tar.gz -C /data .

# 备份媒体文件数据卷
docker run --rm -v taiga-media-data:/data -v /www/backup/taiga:/backup alpine tar czf /backup/taiga-media-data.tar.gz -C /data .

# 备份静态文件数据卷
docker run --rm -v taiga-static-data:/data -v /www/backup/taiga:/backup alpine tar czf /backup/taiga-static-data.tar.gz -C /data .
```

### 3. 备份 .env 配置文件

```bash
cp /www/wwwroot/taiga/.env /www/backup/taiga/env-backup-$(date +%Y%m%d).txt
```

## 常见问题排查

如果部署遇到问题，请参考 `TROUBLESHOOTING.md` 文档。

## 系统维护

### 查看容器日志
```bash
# 查看所有容器日志
cd /www/wwwroot/taiga
docker-compose logs

# 查看特定容器日志
docker logs taiga-back
docker logs taiga-gateway
docker logs taiga-events
```

### 重启容器
```bash
cd /www/wwwroot/taiga
docker-compose restart
```

### 停止所有容器
```bash
cd /www/wwwroot/taiga
docker-compose down
```

### 更新 Taiga 镜像
```bash
cd /www/wwwroot/taiga
docker-compose pull
docker-compose up -d
```

## 安全建议

1. **定期更新**：定期更新 Docker 镜像和系统软件包
2. **防火墙配置**：在宝塔安全设置中只开放必要的端口（80、443、SSH）
3. **禁用公开注册**：默认配置已禁用公开注册，仅管理员可创建用户
4. **强密码策略**：使用强密码并定期更换
5. **备份策略**：每日增量备份，每周全量备份
6. **监控告警**：使用宝塔监控功能设置资源使用告警

## 技术支持

如需帮助，请访问：
- Taiga 官方文档：https://docs.taiga.io/
- GitHub 项目仓库：https://github.com/taigaio/taiga-docker

## 许可证

Taiga 遵循 MPL-2.0 和 AGPL-3.0 许可证。
