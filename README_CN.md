# Taiga Docker - 生产环境部署版（中文说明）

本项目是 Taiga 项目管理系统的 Docker 部署版本，已针对**宝塔面板 + 顶级域名**的生产环境进行优化配置。

![Taiga Screenshot](imgs/taiga.jpg)

## 🚀 快速开始

如果您想快速部署 Taiga，请直接查看 **[快速部署指南](QUICK_START.md)**，5 步即可完成部署！

## 📚 完整文档

本项目提供完整的中文部署文档：

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| **[QUICK_START.md](QUICK_START.md)** | 快速部署指南 | 想要快速上手的用户 |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | 完整部署指南 | 需要详细了解每个步骤的用户 |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | 故障排查指南 | 遇到问题需要解决的用户 |
| **[BAOTA_NGINX_CONFIG.txt](BAOTA_NGINX_CONFIG.txt)** | Nginx 配置示例 | 需要配置反向代理的用户 |
| **[CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)** | 配置修改摘要 | 想了解所有修改内容的用户 |

## ✨ 主要特性

本部署版本已针对生产环境进行以下优化：

✅ **使用 HTTPS 和 WSS 安全协议**
✅ **非默认端口配置（9090:8080）**
✅ **容器自动重启策略**
✅ **完善的备份策略**
✅ **详细的中文文档**
✅ **故障排查指南**
✅ **宝塔面板优化配置**

## 🎯 适用场景

本部署方案适用于以下场景：

- 使用宝塔面板管理的服务器
- 使用顶级域名部署（如：yourdomain.com）
- 需要 HTTPS 安全连接
- 不需要配置邮件服务器（默认使用 console 输出）
- 需要中文部署文档的用户

## 📋 部署要求

### 服务器配置

- **CPU**：2 核或更多
- **内存**：4GB 或更多
- **磁盘**：40GB 或更多可用空间
- **操作系统**：主流 Linux 发行版（Ubuntu、CentOS、Debian 等）

### 软件要求

- **宝塔面板**：7.7.0 或更高版本
- **Docker**：20.10+ 或更高版本
- **Docker Compose**：1.29+ 或 Docker Compose V2
- **Nginx**：1.20 或更高版本

### 域名要求

- 已购买顶级域名
- DNS 已解析到服务器 IP
- 可以申请 SSL 证书（Let's Encrypt 免费证书）

## 🔧 核心配置

本项目的核心配置如下：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 协议 | HTTPS / WSS | 安全加密传输 |
| 域名类型 | 顶级域名 | 如：yourdomain.com |
| 容器端口 | 9090:8080 | 宿主机:容器内部 |
| 反向代理 | http://127.0.0.1:9090 | 宝塔 Nginx 转发目标 |
| 邮件后端 | console | 不需要 SMTP 服务器 |

## 🛠️ 部署流程概述

### 1. 修改配置文件

编辑 `.env` 文件，修改以下关键配置：

```bash
# 改为您的实际域名
TAIGA_DOMAIN=yourdomain.com

# 生成强随机密钥
SECRET_KEY="your-random-50-character-secret-key"

# 设置强密码
POSTGRES_PASSWORD=your-strong-password
RABBITMQ_PASS=your-strong-password
RABBITMQ_ERLANG_COOKIE=your-unique-cookie
```

### 2. 启动 Docker 容器

```bash
cd /www/wwwroot/taiga
chmod 755 launch-taiga.sh taiga-manage.sh
bash launch-taiga.sh
```

### 3. 创建管理员账户

```bash
bash taiga-manage.sh createsuperuser
```

### 4. 配置宝塔面板

- 添加网站（域名）
- 申请 SSL 证书
- 配置反向代理

### 5. 验证部署

访问 `https://yourdomain.com` 并登录测试

详细步骤请参考 **[DEPLOYMENT.md](DEPLOYMENT.md)**

## 🔐 安全配置

**必须修改的安全配置：**

1. **SECRET_KEY**：生成 50 位以上随机字符串
2. **POSTGRES_PASSWORD**：数据库强密码
3. **RABBITMQ_PASS**：消息队列强密码
4. **RABBITMQ_ERLANG_COOKIE**：唯一随机值

**生成随机密钥的命令：**

```bash
# 生成 SECRET_KEY（50 字符）
openssl rand -base64 50

# 生成密码（32 字符）
openssl rand -base64 32
```

## 📦 包含的服务

本 Docker Compose 方案包含以下 9 个服务：

| 服务 | 说明 |
|------|------|
| taiga-db | PostgreSQL 数据库 |
| taiga-back | 后端 API 服务 |
| taiga-async | 异步任务处理 |
| taiga-async-rabbitmq | 异步任务消息队列 |
| taiga-front | 前端界面 |
| taiga-events | WebSocket 实时事件 |
| taiga-events-rabbitmq | 事件消息队列 |
| taiga-protected | 受保护的媒体文件服务 |
| taiga-gateway | Nginx 网关 |

所有服务都配置了自动重启策略（`restart: always`）。

## 🔍 常见问题

### Q: 容器启动失败？

查看日志：
```bash
docker-compose logs
```

详细排查请参考 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Q: 无法访问网站？

检查：
- 防火墙是否开放 80 和 443 端口
- DNS 解析是否生效
- 反向代理配置是否正确

### Q: WebSocket 连接失败？

检查：
- Nginx 配置是否包含 WebSocket 支持
- `.env` 中 `WEBSOCKETS_SCHEME=wss`
- taiga-events 容器是否正常运行

### Q: 如何备份数据？

参考 [DEPLOYMENT.md](DEPLOYMENT.md) 第九步：备份配置

## 📞 获取帮助

如果您在部署过程中遇到问题：

1. **查阅文档**：
   - [DEPLOYMENT.md](DEPLOYMENT.md) - 详细部署步骤
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 常见问题解决

2. **官方资源**：
   - [Taiga 官方文档](https://docs.taiga.io/)
   - [Taiga 社区](https://community.taiga.io/)
   - [GitHub Issues](https://github.com/taigaio/taiga-docker/issues)

3. **日志分析**：
   ```bash
   docker-compose logs -f
   docker logs taiga-back
   docker logs taiga-events
   ```

## 🔄 维护和更新

### 查看容器状态
```bash
docker ps -a
```

### 重启服务
```bash
docker-compose restart
```

### 更新镜像
```bash
docker-compose pull
docker-compose up -d
```

### 查看日志
```bash
docker-compose logs -f
```

## 📄 许可证

Taiga 遵循以下许可证：
- [MPL 2.0](LICENSE)
- [AGPL-3.0](DCOLICENSE)

## 🤝 贡献

欢迎贡献代码、文档或提出问题！

- [贡献指南](CONTRIBUTING.md)
- [行为准则](https://github.com/taigaio/code-of-conduct/blob/main/CODE_OF_CONDUCT.md)

## 🌟 关于 Taiga

Taiga 是一个开源的敏捷项目管理平台，支持 Scrum 和 Kanban 方法论。

- **官网**：https://www.taiga.io/
- **文档**：https://docs.taiga.io/
- **社区**：https://community.taiga.io/
- **Twitter**：[@taigaio](https://twitter.com/taigaio)

---

## 📝 版本说明

本配置基于 Taiga 官方 Docker 部署方案，针对以下场景优化：

- ✅ 宝塔面板管理的服务器
- ✅ 顶级域名部署
- ✅ HTTPS 安全连接
- ✅ 非 80 端口配置
- ✅ 容器自动重启
- ✅ 完善的中文文档

**配置版本**：2024 生产环境优化版

---

**祝您部署成功！** 🎉

有任何问题，请查阅文档或访问 Taiga 社区获取支持。
