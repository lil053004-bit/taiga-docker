# Taiga 快速部署指南

这是一个简化的部署流程，帮助您快速上手。详细说明请参考 `DEPLOYMENT.md`。

## 预检查清单

- [ ] 宝塔面板已安装 Docker 和 Docker Compose
- [ ] 宝塔面板已安装 Nginx
- [ ] 域名 DNS 已解析到服务器
- [ ] 服务器配置：至少 2核CPU、4GB内存

## 5 步快速部署

### 1️⃣ 修改配置文件

编辑 `.env` 文件，修改以下内容：

```bash
# 改为你的域名（不带 http:// 和端口）
TAIGA_DOMAIN=yourdomain.com

# 生成随机密钥（使用命令：openssl rand -base64 50）
SECRET_KEY="your-random-secret-key-50-characters"

# 设置强密码（使用命令：openssl rand -base64 32）
POSTGRES_PASSWORD=your-strong-password
RABBITMQ_PASS=your-strong-password
RABBITMQ_ERLANG_COOKIE=your-unique-cookie
```

### 2️⃣ 启动 Docker 容器

```bash
# 进入项目目录
cd /www/wwwroot/taiga

# 设置执行权限
chmod 755 launch-taiga.sh taiga-manage.sh

# 启动所有容器
bash launch-taiga.sh

# 等待 3-5 分钟，然后检查容器状态
docker ps
```

你应该看到 7 个容器在运行。

### 3️⃣ 创建管理员账户

```bash
# 在项目目录执行
bash taiga-manage.sh createsuperuser

# 按提示输入用户名、邮箱和密码
```

### 4️⃣ 配置宝塔面板

**添加网站：**
1. 宝塔面板 → 网站 → 添加站点
2. 域名填写：`yourdomain.com`（可添加 www 子域名）
3. PHP 版本：纯静态
4. 提交

**申请 SSL 证书：**
1. 网站设置 → SSL → Let's Encrypt
2. 勾选域名 → 申请
3. 开启"强制 HTTPS"

**配置反向代理：**
1. 网站设置 → 配置文件
2. 在 `server { }` 块内添加配置（参考 `BAOTA_NGINX_CONFIG.txt`）
3. 保存并重载 Nginx

### 5️⃣ 验证部署

1. 访问：`https://yourdomain.com`
2. 使用管理员账户登录
3. 创建测试项目
4. 打开浏览器 F12 → 网络，检查 WebSocket 连接（wss://yourdomain.com/events）

## 核心配置要点

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 宿主机端口 | 9090 | Docker 映射到宿主机的端口 |
| 容器端口 | 8080 | 容器内 Nginx 监听端口 |
| 反向代理目标 | http://127.0.0.1:9090 | 宝塔 Nginx 转发目标 |
| 域名协议 | https | 启用 SSL |
| WebSocket 协议 | wss | 安全 WebSocket |

## 快速命令参考

```bash
# 查看容器状态
docker ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 启动服务
docker-compose start

# 备份数据库
docker run --rm -v taiga-db-data:/data -v /www/backup:/backup alpine tar czf /backup/taiga-db-backup.tar.gz -C /data .
```

## 常见问题

**Q: 容器启动失败？**
```bash
# 查看日志找出原因
docker-compose logs

# 检查端口占用
netstat -tulnp | grep 9090
```

**Q: 无法访问网站？**
- 检查防火墙是否开放 80 和 443 端口
- 检查 DNS 解析是否生效
- 检查反向代理配置是否正确

**Q: WebSocket 连接失败？**
- 确保 Nginx 配置包含 WebSocket 支持
- 检查 `.env` 中 `WEBSOCKETS_SCHEME=wss`
- 查看 taiga-events 容器日志

**Q: 文件上传失败？**
- 检查 Nginx 配置中 `client_max_body_size 100M;`
- 重启 taiga-gateway 容器

## 获取帮助

- **详细部署指南**：`DEPLOYMENT.md`
- **故障排查**：`TROUBLESHOOTING.md`
- **Nginx 配置示例**：`BAOTA_NGINX_CONFIG.txt`
- **Taiga 官方文档**：https://docs.taiga.io/

## 安全提醒

- ✅ 使用强随机密钥和密码
- ✅ 启用 HTTPS 和强制跳转
- ✅ 定期备份数据
- ✅ 定期更新 Docker 镜像
- ❌ 不要使用默认密码
- ❌ 不要暴露不必要的端口

---

**祝您部署成功！** 🎉

如有问题，请查阅详细文档或访问 Taiga 社区获取支持。
