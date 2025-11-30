# Taiga 部署检查清单

使用此清单确保您已完成所有部署步骤，避免遗漏关键配置。

## 📋 部署前准备

### 服务器环境检查

- [ ] 服务器配置满足要求（2核CPU、4GB内存、40GB磁盘）
- [ ] 已安装宝塔面板（版本 7.7.0+）
- [ ] 已通过宝塔安装 Docker
- [ ] 已通过宝塔安装 Docker Compose
- [ ] 已通过宝塔安装 Nginx（版本 1.20+）
- [ ] 防火墙已开放 80 和 443 端口
- [ ] SSH 可以正常连接到服务器

### 域名准备

- [ ] 已购买顶级域名
- [ ] DNS A 记录已添加，指向服务器 IP
- [ ] DNS 解析已生效（可通过 `ping yourdomain.com` 验证）
- [ ] 域名可以正常访问（测试 HTTP 连接）

## 🔧 配置文件修改

### .env 文件修改检查

- [ ] 已将 `TAIGA_DOMAIN` 改为实际域名（不带 http:// 和端口）
- [ ] 已确认 `TAIGA_SCHEME=https`
- [ ] 已确认 `WEBSOCKETS_SCHEME=wss`
- [ ] 已确认 `SUBPATH=""`（空字符串）
- [ ] 已生成并设置 `SECRET_KEY`（50 位以上随机字符串）
- [ ] 已生成并设置 `POSTGRES_PASSWORD`（强密码）
- [ ] 已生成并设置 `RABBITMQ_PASS`（强密码）
- [ ] 已生成并设置 `RABBITMQ_ERLANG_COOKIE`（唯一随机值）
- [ ] 已确认 `EMAIL_BACKEND=console`
- [ ] 已删除末尾的 Supabase 配置（如果存在）

**验证命令：**
```bash
grep "TAIGA_SCHEME=https" .env
grep "WEBSOCKETS_SCHEME=wss" .env
grep "TAIGA_DOMAIN=" .env | grep -v "localhost"
```

### docker-compose.yml 检查

- [ ] taiga-gateway 端口映射为 `"9090:8080"`
- [ ] 所有服务都有 `restart: always` 配置（应该有 9 个）

**验证命令：**
```bash
grep "9090:8080" docker-compose.yml
grep -c "restart: always" docker-compose.yml  # 应输出 9
```

### taiga-gateway/taiga.conf 检查

- [ ] listen 端口为 `8080 default_server`

**验证命令：**
```bash
grep "listen 8080" taiga-gateway/taiga.conf
```

## 📤 文件上传

- [ ] 整个项目文件夹已上传到服务器（推荐：`/www/wwwroot/taiga`）
- [ ] `.env` 文件存在且配置正确
- [ ] `docker-compose.yml` 文件存在
- [ ] `docker-compose-inits.yml` 文件存在
- [ ] `launch-taiga.sh` 文件存在
- [ ] `taiga-manage.sh` 文件存在
- [ ] `taiga-gateway/taiga.conf` 文件存在
- [ ] 脚本文件已设置执行权限（`chmod 755 *.sh`）

**验证命令：**
```bash
cd /www/wwwroot/taiga
ls -la *.sh
ls -la taiga-gateway/taiga.conf
```

## 🐳 Docker 容器启动

- [ ] 已进入项目目录（`cd /www/wwwroot/taiga`）
- [ ] 已执行 `chmod 755 launch-taiga.sh taiga-manage.sh`
- [ ] 已执行 `bash launch-taiga.sh`
- [ ] 已等待 3-5 分钟让容器启动完成
- [ ] 已执行 `docker ps` 验证所有容器在运行
- [ ] 看到 9 个容器状态为 "Up"
- [ ] taiga-db 容器健康状态为 "healthy"

**验证命令：**
```bash
docker ps
docker ps | wc -l  # 应该显示 10（包含标题行）
```

**预期看到的容器：**
1. taiga-db
2. taiga-back
3. taiga-async
4. taiga-async-rabbitmq
5. taiga-front
6. taiga-events
7. taiga-events-rabbitmq
8. taiga-protected
9. taiga-gateway

## 👤 管理员账户创建

- [ ] 已执行 `bash taiga-manage.sh createsuperuser`
- [ ] 已输入管理员用户名
- [ ] 已输入管理员邮箱
- [ ] 已设置管理员密码（并确认）
- [ ] 管理员凭据已记录到安全位置

**提示：** 如果创建失败，请检查容器是否全部启动完成。

## 🌐 宝塔面板网站配置

### 添加网站

- [ ] 已在宝塔面板点击"网站" → "添加站点"
- [ ] 已填写域名（如：`yourdomain.com`）
- [ ] 已添加 www 子域名（如：`www.yourdomain.com`）
- [ ] PHP 版本已选择"纯静态"
- [ ] 网站已成功创建

### SSL 证书配置

- [ ] 已进入网站设置 → SSL
- [ ] 已选择 Let's Encrypt
- [ ] 已勾选域名和 www 域名
- [ ] 证书已申请成功
- [ ] 已开启"强制 HTTPS"选项
- [ ] SSL 证书状态显示为"有效"

### 反向代理配置

- [ ] 已进入网站设置 → 配置文件
- [ ] 已在 `server { }` 块内添加反向代理配置
- [ ] 配置包含 `client_max_body_size 100M;`
- [ ] 配置包含主应用反向代理（`location /`）
- [ ] 配置包含 WebSocket 支持（`location /events`）
- [ ] 已保存配置文件
- [ ] 已重载 Nginx

**参考：** `BAOTA_NGINX_CONFIG.txt` 文件

## ✅ 部署验证

### 基础访问测试

- [ ] 可以通过 `https://yourdomain.com` 访问
- [ ] 看到 Taiga 登录页面
- [ ] 页面加载完整，无错误
- [ ] 使用管理员账户可以成功登录
- [ ] 可以创建测试项目

### WebSocket 连接测试

- [ ] 打开浏览器开发者工具（F12）
- [ ] 切换到"网络"（Network）标签
- [ ] 过滤 WS（WebSocket）连接
- [ ] 看到 `wss://yourdomain.com/events` 连接
- [ ] 连接状态为 101（协议切换成功）
- [ ] 连接保持活跃，无断开

### 功能测试

- [ ] 可以创建新项目
- [ ] 可以创建任务（Story/Task）
- [ ] 可以上传附件（测试文件上传）
- [ ] 实时更新功能正常（WebSocket）
- [ ] 可以编辑和删除内容
- [ ] 可以邀请成员（如果需要）

### 性能检查

- [ ] 页面加载速度正常（< 3 秒）
- [ ] 操作响应及时
- [ ] 无明显卡顿或延迟
- [ ] 浏览器控制台无错误信息

## 🔒 安全加固

- [ ] 所有默认密码已更换
- [ ] SECRET_KEY 使用强随机值
- [ ] 数据库密码使用强密码
- [ ] RabbitMQ 密码使用强密码
- [ ] HTTPS 强制跳转已启用
- [ ] 防火墙只开放必要端口（80、443、SSH）
- [ ] SSH 端口已修改（可选，建议）
- [ ] 宝塔面板已设置强密码
- [ ] 宝塔面板端口已修改（可选，建议）

## 💾 备份配置

- [ ] 已了解备份策略（参考 DEPLOYMENT.md）
- [ ] 已测试数据库备份命令
- [ ] 已测试媒体文件备份命令
- [ ] 已备份 .env 配置文件
- [ ] 已在宝塔面板设置计划任务备份（可选）
- [ ] 已确定备份存储位置
- [ ] 已设置备份保留策略

**备份命令测试：**
```bash
# 创建备份目录
mkdir -p /www/backup/taiga

# 测试数据库备份
docker run --rm -v taiga-db-data:/data -v /www/backup/taiga:/backup alpine tar czf /backup/taiga-db-test.tar.gz -C /data .

# 验证备份文件
ls -lh /www/backup/taiga/
```

## 📊 监控设置

- [ ] 已在宝塔面板查看服务器监控
- [ ] 已了解如何查看容器日志
- [ ] 已了解如何重启容器
- [ ] 已设置资源使用告警（可选）
- [ ] 已添加 SSL 证书到期提醒

**日志查看命令：**
```bash
# 查看所有容器日志
docker-compose logs -f

# 查看特定容器日志
docker logs taiga-back
docker logs taiga-events
docker logs taiga-gateway
```

## 📚 文档归档

- [ ] 已保存所有管理员凭据到安全位置
- [ ] 已保存 .env 配置文件副本
- [ ] 已记录服务器 IP 和域名
- [ ] 已记录宝塔面板访问地址
- [ ] 已记录所有修改过的密码
- [ ] 已保存部署文档（DEPLOYMENT.md 等）

## 🎓 团队培训

- [ ] 管理员已熟悉 Taiga 基本操作
- [ ] 管理员已了解如何创建项目
- [ ] 管理员已了解如何邀请用户
- [ ] 管理员已了解如何查看日志
- [ ] 管理员已了解如何重启服务
- [ ] 管理员已阅读故障排查文档（TROUBLESHOOTING.md）

## 🚀 上线准备

- [ ] 所有功能测试通过
- [ ] 性能测试通过
- [ ] 安全检查通过
- [ ] 备份策略已实施
- [ ] 监控已配置
- [ ] 文档已归档
- [ ] 团队已培训
- [ ] 准备正式上线使用

---

## ✅ 检查清单总结

### 关键步骤（必须完成）

1. ✅ 修改 .env 文件（域名、密钥、密码）
2. ✅ 上传文件到服务器
3. ✅ 启动 Docker 容器
4. ✅ 创建管理员账户
5. ✅ 配置宝塔网站和 SSL
6. ✅ 配置反向代理
7. ✅ 验证部署成功
8. ✅ 配置备份策略

### 可选步骤（建议完成）

- 修改 SSH 端口
- 修改宝塔面板端口
- 设置资源使用告警
- 配置自动备份任务
- 进行压力测试

---

## 🆘 遇到问题？

如果检查清单中任何一项未通过，请：

1. **查看对应的文档章节**：
   - [DEPLOYMENT.md](DEPLOYMENT.md) - 详细部署步骤
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排查

2. **检查日志**：
   ```bash
   docker-compose logs -f
   ```

3. **验证配置**：
   - 重新检查 .env 文件
   - 验证 Nginx 配置
   - 确认容器状态

4. **寻求帮助**：
   - Taiga 官方文档：https://docs.taiga.io/
   - Taiga 社区：https://community.taiga.io/
   - GitHub Issues：https://github.com/taigaio/taiga-docker/issues

---

**完成所有检查项后，您的 Taiga 实例就可以正式投入使用了！** 🎉

请定期检查此清单，确保系统持续稳定运行。
