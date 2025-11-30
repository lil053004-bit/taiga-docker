# Taiga 部署故障排查指南

本文档提供 Taiga 部署过程中常见问题的排查和解决方法。

## 目录

1. [容器启动问题](#容器启动问题)
2. [网络连接问题](#网络连接问题)
3. [数据库连接问题](#数据库连接问题)
4. [WebSocket 连接问题](#websocket-连接问题)
5. [文件上传问题](#文件上传问题)
6. [SSL 证书问题](#ssl-证书问题)
7. [性能问题](#性能问题)

---

## 容器启动问题

### 问题：执行 launch-taiga.sh 后容器无法启动

**症状**：
- 容器启动失败
- `docker ps` 看不到容器或容器状态为 Exited

**排查步骤**：

1. **检查容器日志**
```bash
cd /www/wwwroot/taiga
docker-compose logs
```

2. **查看特定容器的详细日志**
```bash
docker logs taiga-db
docker logs taiga-back
docker logs taiga-gateway
```

3. **检查端口占用**
```bash
# 检查 9090 端口是否被占用
netstat -tulnp | grep 9090
# 或使用
lsof -i :9090
```

**解决方法**：

- 如果端口被占用，修改 `docker-compose.yml` 中的端口映射
- 如果是权限问题，检查文件权限：
```bash
chmod 755 launch-taiga.sh taiga-manage.sh
```

### 问题：taiga-db 容器健康检查失败

**症状**：
- 容器日志显示数据库未就绪
- 其他容器等待 taiga-db 健康检查

**排查步骤**：

1. **检查数据库容器状态**
```bash
docker ps -a | grep taiga-db
```

2. **查看数据库日志**
```bash
docker logs taiga-db
```

3. **手动测试数据库连接**
```bash
docker exec -it taiga-db pg_isready -U taiga
```

**解决方法**：

- 等待更长时间（数据库首次初始化需要 1-2 分钟）
- 检查 `.env` 文件中的 `POSTGRES_PASSWORD` 是否正确
- 如果数据卷损坏，删除数据卷重新初始化：
```bash
docker-compose down -v
bash launch-taiga.sh
```

**警告**：删除数据卷会丢失所有数据，请谨慎操作！

---

## 网络连接问题

### 问题：无法访问 https://yourdomain.com

**症状**：
- 浏览器显示无法连接
- 502 Bad Gateway 错误

**排查步骤**：

1. **检查 Nginx 是否运行**
```bash
# 在宝塔面板查看 Nginx 状态
# 或使用命令行
systemctl status nginx
```

2. **检查 taiga-gateway 容器是否运行**
```bash
docker ps | grep taiga-gateway
```

3. **检查 9090 端口是否监听**
```bash
netstat -tulnp | grep 9090
```

4. **测试本地访问**
```bash
curl http://127.0.0.1:9090
```

**解决方法**：

- 重启 Nginx：
```bash
# 在宝塔面板重启 Nginx
# 或使用命令行
systemctl restart nginx
```

- 重启 taiga-gateway 容器：
```bash
docker restart taiga-gateway
```

- 检查宝塔安全设置，确保 80 和 443 端口已开放

### 问题：显示 404 Not Found

**症状**：
- 可以访问域名，但显示 404 错误

**排查步骤**：

1. **检查反向代理配置**
- 在宝塔面板查看网站设置 → 反向代理
- 确认目标 URL 为 `http://127.0.0.1:9090`

2. **检查 Nginx 配置文件**
```bash
# 查看配置文件
cat /www/server/panel/vhost/nginx/yourdomain.com.conf
```

**解决方法**：

按照 `DEPLOYMENT.md` 第七步重新配置反向代理

---

## 数据库连接问题

### 问题：后端无法连接数据库

**症状**：
- taiga-back 日志显示数据库连接错误
- 无法登录系统

**排查步骤**：

1. **检查数据库容器是否健康**
```bash
docker ps | grep taiga-db
# 查看 STATUS 列是否显示 "healthy"
```

2. **检查数据库密码是否一致**
```bash
# 查看 .env 文件中的密码
cat .env | grep POSTGRES_PASSWORD
```

3. **测试数据库连接**
```bash
docker exec -it taiga-db psql -U taiga -d taiga -c "SELECT 1;"
```

**解决方法**：

- 确保 `.env` 中的 `POSTGRES_PASSWORD` 与初始化时一致
- 如果修改了密码，需要删除数据卷重新初始化（会丢失数据）

---

## WebSocket 连接问题

### 问题：实时更新功能不工作

**症状**：
- 页面需要刷新才能看到更新
- 浏览器控制台显示 WebSocket 连接失败

**排查步骤**：

1. **打开浏览器开发者工具（F12）**
2. **切换到"网络"（Network）标签**
3. **过滤 WS 连接**
4. **查找 `wss://yourdomain.com/events` 连接**

**可能的错误**：
- 连接状态为红色（失败）
- 状态码不是 101（协议切换）

**解决方法**：

1. **检查 .env 配置**
```bash
# 确保以下配置正确
TAIGA_SCHEME=https
TAIGA_DOMAIN=yourdomain.com
WEBSOCKETS_SCHEME=wss
```

2. **检查 Nginx 配置是否包含 WebSocket 支持**

在宝塔面板网站设置 → 配置文件中，确保有以下配置：

```nginx
location /events {
    proxy_pass http://127.0.0.1:9090/events;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_connect_timeout 7d;
    proxy_send_timeout 7d;
    proxy_read_timeout 7d;
}
```

3. **检查 taiga-events 容器是否运行**
```bash
docker ps | grep taiga-events
docker logs taiga-events
```

4. **重启相关容器**
```bash
docker restart taiga-events taiga-events-rabbitmq taiga-gateway
```

---

## 文件上传问题

### 问题：无法上传文件或上传大文件失败

**症状**：
- 上传小文件正常，大文件失败
- 显示 413 Request Entity Too Large

**排查步骤**：

1. **检查 Nginx 配置**
```bash
# 在宝塔面板查看网站配置文件
# 搜索 client_max_body_size
```

2. **检查 taiga-gateway 配置**
```bash
cat /www/wwwroot/taiga/taiga-gateway/taiga.conf | grep client_max_body_size
```

**解决方法**：

1. **在宝塔 Nginx 配置中添加**：
```nginx
client_max_body_size 100M;
```

2. **确保 taiga-gateway/taiga.conf 中已有**：
```nginx
client_max_body_size 100M;
```

3. **重启服务**：
```bash
# 重启宝塔 Nginx
# 重启 taiga-gateway 容器
docker restart taiga-gateway
```

---

## SSL 证书问题

### 问题：无法申请 Let's Encrypt 证书

**症状**：
- 宝塔面板显示证书申请失败

**排查步骤**：

1. **检查域名 DNS 解析**
```bash
ping yourdomain.com
nslookup yourdomain.com
```

2. **检查 80 端口是否可访问**
```bash
curl http://yourdomain.com
```

**解决方法**：

- 确保域名已正确解析到服务器 IP
- 确保防火墙已开放 80 端口
- 在宝塔安全设置中检查 80 端口状态
- 等待 DNS 解析生效（可能需要 10-30 分钟）

### 问题：SSL 证书过期

**症状**：
- 浏览器显示证书无效
- 证书已过期警告

**解决方法**：

Let's Encrypt 证书有效期为 90 天，宝塔面板会自动续期。如果自动续期失败：

1. 在宝塔面板手动续期：
   - 网站设置 → SSL → Let's Encrypt
   - 点击"续签"按钮

2. 如果续期失败，删除旧证书重新申请

---

## 性能问题

### 问题：系统运行缓慢

**症状**：
- 页面加载慢
- 操作响应时间长

**排查步骤**：

1. **检查服务器资源使用**
```bash
# CPU 和内存使用情况
top

# 磁盘使用情况
df -h

# Docker 容器资源使用
docker stats
```

2. **检查数据库性能**
```bash
docker exec -it taiga-db psql -U taiga -d taiga -c "SELECT * FROM pg_stat_activity;"
```

**解决方法**：

1. **优化服务器资源**：
   - 升级服务器配置（建议 2 核 4GB 以上）
   - 清理不必要的进程

2. **优化 Docker 日志**：
```bash
# 限制容器日志大小
# 编辑 /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# 重启 Docker
systemctl restart docker
```

3. **清理 Docker 资源**：
```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune
```

---

## 数据恢复

### 问题：需要恢复备份数据

**步骤**：

1. **停止所有容器**
```bash
cd /www/wwwroot/taiga
docker-compose down
```

2. **删除现有数据卷**
```bash
docker volume rm taiga-db-data taiga-media-data taiga-static-data
```

3. **创建新的数据卷**
```bash
docker volume create taiga-db-data
docker volume create taiga-media-data
docker volume create taiga-static-data
```

4. **恢复备份数据**
```bash
# 恢复数据库
docker run --rm -v taiga-db-data:/data -v /www/backup/taiga:/backup alpine tar xzf /backup/taiga-db-data.tar.gz -C /data

# 恢复媒体文件
docker run --rm -v taiga-media-data:/data -v /www/backup/taiga:/backup alpine tar xzf /backup/taiga-media-data.tar.gz -C /data

# 恢复静态文件
docker run --rm -v taiga-static-data:/data -v /www/backup/taiga:/backup alpine tar xzf /backup/taiga-static-data.tar.gz -C /data
```

5. **启动容器**
```bash
bash launch-taiga.sh
```

---

## 获取更多帮助

### 查看容器完整日志

```bash
cd /www/wwwroot/taiga

# 查看所有容器日志
docker-compose logs -f

# 查看特定容器最近 100 行日志
docker logs --tail 100 taiga-back

# 实时监控日志
docker logs -f taiga-events
```

### 进入容器内部排查

```bash
# 进入后端容器
docker exec -it taiga-back bash

# 进入数据库容器
docker exec -it taiga-db bash

# 进入网关容器
docker exec -it taiga-gateway sh
```

### 重置整个系统（警告：会丢失所有数据）

```bash
cd /www/wwwroot/taiga

# 停止并删除所有容器和数据卷
docker-compose down -v

# 重新启动
bash launch-taiga.sh

# 重新创建管理员
bash taiga-manage.sh createsuperuser
```

---

## 常用命令速查

```bash
# 查看所有容器状态
docker ps -a

# 重启所有服务
docker-compose restart

# 停止所有服务
docker-compose stop

# 启动所有服务
docker-compose start

# 查看容器资源使用
docker stats

# 清理未使用的 Docker 资源
docker system prune -a

# 更新镜像
docker-compose pull
docker-compose up -d

# 查看 Docker 网络
docker network ls
docker network inspect taiga_taiga
```

---

## 联系支持

如果以上方法都无法解决问题，请：

1. 收集以下信息：
   - 完整的错误日志
   - 系统配置信息
   - 复现问题的步骤

2. 访问 Taiga 官方支持：
   - GitHub Issues: https://github.com/taigaio/taiga-docker/issues
   - 官方文档: https://docs.taiga.io/
   - 社区论坛: https://community.taiga.io/

3. 在提问时包含：
   - 操作系统版本
   - Docker 版本
   - Docker Compose 版本
   - Taiga 版本
   - 错误日志片段
