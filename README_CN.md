# Taiga Docker 部署指南

生产环境 Taiga 安装，支持 Docker Compose，具有自动初始化和中文语言支持。

## 快速开始

### 系统要求

- 已安装 Docker 和 Docker Compose
- 配置 HTTPS 的域名（或在 `.env` 中修改为 HTTP）

### 安装步骤

1. **克隆并配置**

```bash
git clone <仓库地址>
cd project
```

2. **更新配置**

编辑 `.env` 文件并设置您的域名：

```bash
TAIGA_DOMAIN=your-domain.com
```

3. **启动 Taiga**

```bash
bash launch-taiga.sh
```

等待 60 秒完成初始化。

4. **访问 Taiga**

- **主界面**: `https://your-domain.com`
- **管理后台**: `https://your-domain.com/admin/`

**默认登录凭据:**
- 用户名: `adsadmin`
- 密码: `A52290120a`

**⚠️ 首次登录后请立即更改默认密码！**

---

## 功能特性

- **自动初始化** - 首次启动时自动创建超级用户
- **中文界面** - 默认使用中文界面
- **自动分配** - 新建项目自动分配给管理员
- **自定义字段显示** - 看板卡片上显示自定义字段
- **HTTPS 就绪** - 预配置安全连接
- **RabbitMQ 已配置** - 事件和异步任务立即可用

---

## 配置说明

### 环境变量

编辑 `.env` 进行配置：

```bash
# 域名配置
TAIGA_DOMAIN=your-domain.com
TAIGA_SCHEME=https

# 数据库
POSTGRES_USER=taiga
POSTGRES_PASSWORD=A52290120a

# RabbitMQ
RABBITMQ_USER=taiga
RABBITMQ_PASS=A52290120a
RABBITMQ_VHOST=taiga

# 管理员用户（自动创建）
AUTO_ASSIGN_ADMIN_USERNAME=adsadmin
AUTO_ASSIGN_ADMIN_EMAIL=your-email@example.com
```

### Nginx/反向代理

如果使用 nginx 作为反向代理，请配置转发到端口 9090：

```nginx
location / {
    proxy_pass http://localhost:9090;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /events {
    proxy_pass http://localhost:9090/events;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

---

## 管理命令

### 查看日志

```bash
docker compose logs -f
```

### 检查服务状态

```bash
docker compose ps
```

### 重启服务

```bash
docker compose restart
```

### 停止服务

```bash
docker compose down
```

### 数据库备份

```bash
docker exec project-taiga-db-1 pg_dump -U taiga taiga > backup.sql
```

### 运行 Django 管理命令

```bash
bash taiga-manage.sh <命令>

# 示例:
bash taiga-manage.sh migrate
bash taiga-manage.sh createsuperuser
bash taiga-manage.sh shell
```

---

## 自定义功能

### 自动分配

新的用户故事、任务和问题会自动分配给管理员用户。在 `.env` 中配置：

```bash
AUTO_ASSIGN_ENABLED=True
AUTO_ASSIGN_ADMIN_USERNAME=adsadmin
```

### 自定义字段显示

自定义字段自动显示在：
- 看板卡片
- 待办事项
- 任务列表

在 `taiga-front/custom-fields.js` 中配置。

### 中文语言

所有用户默认设置为中文（zh-Hans）。系统包括：
- 中文界面翻译
- 中文自定义字段标签
- 中文日期格式

---

## 故障排除

### 服务无法启动

```bash
# 查看日志
docker compose logs --tail 100

# 重启所有服务
docker compose down
bash launch-taiga.sh
```

### 无法登录管理后台

超级用户在首次启动时自动创建。如果登录失败：

```bash
# 重新创建超级用户
docker compose exec taiga-back python manage.py initialize_taiga

# 检查用户是否存在
docker compose exec taiga-back python manage.py shell -c \
  "from django.contrib.auth import get_user_model; \
   User = get_user_model(); \
   print(User.objects.filter(username='adsadmin').exists())"
```

### RabbitMQ 连接错误

如果看到 RabbitMQ 连接错误：

```bash
# 停止并删除卷
docker compose down
docker volume rm project_taiga-events-rabbitmq-data
docker volume rm project_taiga-async-rabbitmq-data

# 重启
bash launch-taiga.sh
```

### 数据库连接问题

```bash
# 检查数据库是否运行
docker compose ps taiga-db

# 查看数据库日志
docker compose logs taiga-db --tail 50
```

### 端口已被占用

如果端口 9090 已被占用，编辑 `docker-compose.yml`：

```yaml
taiga-gateway:
  ports:
    - "8080:8080"  # 将 9090 更改为任何可用端口
```

---

## 系统架构

### 服务

- **taiga-db** - PostgreSQL 数据库
- **taiga-back** - Django 后端 API
- **taiga-async** - Celery 异步任务处理
- **taiga-front** - Angular 前端
- **taiga-events** - WebSocket 事件服务器
- **taiga-gateway** - Nginx 反向代理
- **taiga-protected** - 附件保护服务器
- **taiga-events-rabbitmq** - 事件队列 RabbitMQ
- **taiga-async-rabbitmq** - 异步任务队列 RabbitMQ

### 数据卷

- **taiga-db-data** - 数据库文件
- **taiga-static-data** - 静态资源
- **taiga-media-data** - 用户上传
- **taiga-events-rabbitmq-data** - 事件队列
- **taiga-async-rabbitmq-data** - 异步队列

### 自定义集成

`taiga-custom` 目录包含 Django 自定义功能：
- 自动分配信号
- 自定义字段序列化器
- 管理命令
- 管理界面扩展

---

## 更新

### 更新 Docker 镜像

```bash
docker compose pull
docker compose down
docker compose up -d
```

### 更新前备份

```bash
# 备份数据库
docker exec project-taiga-db-1 pg_dump -U taiga taiga > backup_$(date +%Y%m%d).sql

# 备份媒体文件
docker cp project-taiga-back-1:/taiga-back/media ./media_backup
```

---

## 安全性

### 更改默认凭据

首次登录后，立即更改默认密码：

1. 访问 `https://your-domain.com/admin/`
2. 使用 `adsadmin` / `A52290120a` 登录
3. 点击右上角的用户名
4. 选择"修改密码"

### 更新密钥

生成新的密钥并更新 `.env`：

```bash
SECRET_KEY="your-new-random-secret-key-here"
```

然后重启服务：

```bash
docker compose restart taiga-back taiga-async
```

### HTTPS 配置

确保您的反向代理（nginx/Caddy）终止 SSL 并设置：
- `X-Forwarded-Proto: https`
- `X-Forwarded-For` 头
- `Host` 头

---

## 支持

### 文档

- [官方 Taiga 文档](https://docs.taiga.io/)
- [Docker 设置指南](https://github.com/taigaio/taiga-docker)

### 获取帮助

- 查看日志: `docker compose logs -f`
- 检查 `.env` 配置
- 确保所有服务正在运行: `docker compose ps`

---

## 许可证

此设置包括：
- Taiga: MPL-2.0 许可证
- 自定义扩展: 参见 `LICENSE` 文件

---

## 维护

### 每周

- 检查错误日志: `docker compose logs --tail 100`
- 验证所有服务运行: `docker compose ps`

### 每月

- 备份数据库
- 更新 Docker 镜像
- 清理旧会话: `bash taiga-manage.sh clearsessions`

### 按需

- 监控磁盘空间（Docker 卷）
- 查看和轮换日志
- 更新自定义扩展

---

**享受使用 Taiga！🎉**

如有问题，请先查看日志: `docker compose logs -f`
