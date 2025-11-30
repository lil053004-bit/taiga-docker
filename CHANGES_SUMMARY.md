# 配置文件修改摘要

本文档总结了为生产环境部署所做的所有配置修改。

## 修改的文件

### 1. `.env` 环境变量配置文件

**修改内容：**

| 配置项 | 原值 | 新值 | 说明 |
|--------|------|------|------|
| `TAIGA_SCHEME` | `http` | `https` | 启用 HTTPS 协议 |
| `TAIGA_DOMAIN` | `localhost:9000` | `yourdomain.com` | 改为实际域名（需用户替换） |
| `SUBPATH` | `""` | `""` | 保持为空（顶级域名） |
| `WEBSOCKETS_SCHEME` | `ws` | `wss` | 启用安全 WebSocket |
| `SECRET_KEY` | `taiga-secret-key` | `taiga-prod-secret-key-change-this-to-random-50-chars` | 提示需更换为强随机密钥 |
| `POSTGRES_PASSWORD` | `taiga` | `taiga-strong-password-change-this` | 提示需更换为强密码 |
| `RABBITMQ_PASS` | `taiga` | `rabbitmq-strong-password-change-this` | 提示需更换为强密码 |
| `RABBITMQ_ERLANG_COOKIE` | `secret-erlang-cookie` | `unique-erlang-cookie-change-this-to-random-value` | 提示需更换为唯一值 |

**删除内容：**
- `VITE_SUPABASE_URL`（不需要 Supabase）
- `VITE_SUPABASE_SUPABASE_ANON_KEY`（不需要 Supabase）

### 2. `docker-compose.yml` Docker 编排配置文件

**修改内容：**

1. **端口映射修改（taiga-gateway 服务）：**
   - 原值：`"9000:80"`
   - 新值：`"9090:8080"`
   - 说明：避免使用默认 80 端口，宿主机使用 9090，容器内使用 8080

2. **添加自动重启策略（所有服务）：**
   - 为所有 9 个服务添加了 `restart: always`
   - 包括：taiga-db, taiga-back, taiga-async, taiga-async-rabbitmq, taiga-front, taiga-events, taiga-events-rabbitmq, taiga-protected, taiga-gateway
   - 说明：确保服务器重启后容器自动启动

### 3. `taiga-gateway/taiga.conf` Nginx 网关配置文件

**修改内容：**

| 配置项 | 原值 | 新值 | 说明 |
|--------|------|------|------|
| `listen` | `80 default_server` | `8080 default_server` | 容器内 Nginx 监听 8080 端口 |

## 新增的文件

### 1. `DEPLOYMENT.md`
完整的生产环境部署指南，包含：
- 环境准备要求
- 详细的 9 步部署流程
- 配置说明和示例
- 备份策略
- 安全建议
- 维护命令

### 2. `TROUBLESHOOTING.md`
故障排查指南，包含：
- 容器启动问题
- 网络连接问题
- 数据库连接问题
- WebSocket 连接问题
- 文件上传问题
- SSL 证书问题
- 性能优化
- 数据恢复步骤
- 常用命令速查

### 3. `BAOTA_NGINX_CONFIG.txt`
宝塔面板 Nginx 反向代理配置示例：
- 完整的反向代理规则
- WebSocket 支持配置
- 文件上传大小限制
- 配置步骤说明

### 4. `QUICK_START.md`
快速部署指南：
- 简化的 5 步部署流程
- 核心配置要点表格
- 快速命令参考
- 常见问题 FAQ
- 安全提醒清单

### 5. `CHANGES_SUMMARY.md`（本文件）
配置修改摘要文档

## 部署架构

```
用户访问
    ↓
https://yourdomain.com (443端口)
    ↓
宝塔 Nginx（SSL 终止，反向代理）
    ↓
http://127.0.0.1:9090
    ↓
Docker 容器 taiga-gateway (8080端口)
    ↓
内部微服务（taiga-front, taiga-back, taiga-events, etc.）
```

## 端口使用说明

| 端口 | 位置 | 说明 |
|------|------|------|
| 443 | 宝塔 Nginx | 外部 HTTPS 访问（公开） |
| 80 | 宝塔 Nginx | HTTP 自动跳转到 HTTPS（公开） |
| 9090 | 宿主机 | Docker 映射端口（内部） |
| 8080 | taiga-gateway 容器内 | Nginx 监听端口（内部） |

## 安全改进

1. ✅ 启用 HTTPS 和 WSS（安全传输）
2. ✅ 使用非默认端口（避免常见扫描）
3. ✅ 提示用户更换默认密码（增强安全性）
4. ✅ 容器自动重启（提高可用性）
5. ✅ 删除不必要的 Supabase 配置（减少混淆）

## 用户需要做的配置

在使用前，用户必须修改 `.env` 文件中的以下内容：

### 必须修改：

1. **域名**：
   ```
   TAIGA_DOMAIN=yourdomain.com  # 替换为实际域名
   ```

2. **密钥和密码**（建议使用 `openssl rand -base64 X` 生成）：
   ```
   SECRET_KEY="your-random-50-character-secret-key"
   POSTGRES_PASSWORD=your-strong-password
   RABBITMQ_PASS=your-strong-password
   RABBITMQ_ERLANG_COOKIE=your-unique-cookie
   ```

### 生成命令：

```bash
# 生成 SECRET_KEY（50 字符）
openssl rand -base64 50

# 生成各种密码（32 字符）
openssl rand -base64 32
```

## 验证配置正确性

### 检查 .env 文件：
```bash
grep "TAIGA_SCHEME=https" .env
grep "WEBSOCKETS_SCHEME=wss" .env
grep "TAIGA_DOMAIN=" .env | grep -v "localhost"
```

### 检查 docker-compose.yml：
```bash
grep "9090:8080" docker-compose.yml
grep -c "restart: always" docker-compose.yml  # 应该输出 9
```

### 检查 taiga.conf：
```bash
grep "listen 8080" taiga-gateway/taiga.conf
```

## 兼容性说明

- ✅ 兼容宝塔面板 7.7.0+
- ✅ 兼容 Docker 20.10+
- ✅ 兼容 Docker Compose 1.29+ 或 Docker Compose V2
- ✅ 支持所有主流 Linux 发行版（Ubuntu, CentOS, Debian 等）
- ✅ 支持顶级域名和子域名部署

## 下一步

1. **阅读**：`QUICK_START.md` - 了解快速部署流程
2. **配置**：修改 `.env` 文件中的必要参数
3. **部署**：按照 `DEPLOYMENT.md` 中的步骤执行
4. **验证**：确保所有功能正常工作
5. **备份**：设置定期备份策略

## 技术支持

如有问题，请参考：
- `DEPLOYMENT.md` - 详细部署指南
- `TROUBLESHOOTING.md` - 故障排查指南
- `QUICK_START.md` - 快速开始指南
- Taiga 官方文档：https://docs.taiga.io/
- GitHub 仓库：https://github.com/taigaio/taiga-docker

---

**所有配置已完成，项目已准备好部署！** ✅
