# 🚀 从这里开始 - Taiga 生产环境部署

欢迎使用 Taiga Docker 生产环境部署包！本文档将指导您快速找到所需的文档。

---

## 📂 项目已准备就绪

✅ **所有配置文件已优化完成**
✅ **完整的中文文档已准备**
✅ **适配宝塔面板 + 顶级域名部署**

---

## 🎯 根据您的需求选择文档

### 😊 我想快速部署，不想看太多文档

👉 **直接查看：[QUICK_START.md](QUICK_START.md)**

这个文档提供了最简洁的 5 步部署流程，让您快速上手。

---

### 🤓 我想详细了解每一个步骤

👉 **详细阅读：[DEPLOYMENT.md](DEPLOYMENT.md)**

这个文档提供了完整的 9 步部署指南，包含详细说明和示例。

---

### 🔧 我想检查是否遗漏了配置

👉 **使用检查清单：[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**

这个文档提供了完整的检查清单，确保您不会遗漏任何步骤。

---

### 🆘 我遇到了问题需要排查

👉 **查看故障排查：[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

这个文档包含常见问题的解决方法和排查步骤。

---

### 📝 我想了解具体修改了哪些配置

👉 **查看修改摘要：[CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)**

这个文档总结了所有修改的配置项和新增的文件。

---

### 🌐 我需要宝塔面板的 Nginx 配置

👉 **查看配置示例：[BAOTA_NGINX_CONFIG.txt](BAOTA_NGINX_CONFIG.txt)**

这个文件包含完整的宝塔 Nginx 反向代理配置。

---

### 📖 我想了解项目整体情况

👉 **阅读中文说明：[README_CN.md](README_CN.md)**

这个文档提供了项目的整体介绍和特性说明。

---

## ⚡ 超快速开始（3 分钟了解）

### 第 1 步：修改配置（必须！）

编辑 `.env` 文件，修改以下内容：

```bash
# 1. 改为您的域名
TAIGA_DOMAIN=yourdomain.com

# 2. 生成并替换密钥（使用命令：openssl rand -base64 50）
SECRET_KEY="your-random-secret-key"

# 3. 生成并替换密码（使用命令：openssl rand -base64 32）
POSTGRES_PASSWORD=your-password
RABBITMQ_PASS=your-password
RABBITMQ_ERLANG_COOKIE=your-cookie
```

### 第 2 步：启动容器

```bash
cd /www/wwwroot/taiga
chmod 755 *.sh
bash launch-taiga.sh
```

等待 3-5 分钟。

### 第 3 步：创建管理员

```bash
bash taiga-manage.sh createsuperuser
```

### 第 4 步：配置宝塔

1. 添加网站（域名）
2. 申请 SSL 证书
3. 配置反向代理（参考 `BAOTA_NGINX_CONFIG.txt`）

### 第 5 步：访问测试

访问：`https://yourdomain.com`

---

## 🎨 部署架构图

```
用户浏览器
    ↓
https://yourdomain.com (443 端口)
    ↓
宝塔 Nginx（SSL 终止 + 反向代理）
    ↓
http://127.0.0.1:9090
    ↓
Docker 容器 taiga-gateway (8080 端口)
    ↓
内部微服务（前端、后端、WebSocket、数据库等）
```

---

## 📊 核心配置一览

| 配置项 | 值 |
|--------|-----|
| **协议** | HTTPS / WSS |
| **域名** | yourdomain.com（需替换） |
| **宿主机端口** | 9090 |
| **容器端口** | 8080 |
| **反向代理目标** | http://127.0.0.1:9090 |
| **SSL** | Let's Encrypt（宝塔申请） |
| **自动重启** | 已启用（所有容器） |

---

## ✅ 已完成的优化

本部署包已经为您完成以下优化：

✅ **安全协议**：HTTPS + WSS
✅ **端口配置**：使用非默认端口 9090:8080
✅ **自动重启**：所有容器配置 restart: always
✅ **容器配置**：Nginx 监听 8080 端口
✅ **环境变量**：已配置生产环境参数
✅ **文档完善**：7 个中文文档覆盖所有场景

---

## 🔐 安全提醒

**您必须修改的配置（不可跳过）：**

1. ⚠️ **TAIGA_DOMAIN** - 改为您的实际域名
2. ⚠️ **SECRET_KEY** - 改为 50 位随机字符串
3. ⚠️ **POSTGRES_PASSWORD** - 改为强密码
4. ⚠️ **RABBITMQ_PASS** - 改为强密码
5. ⚠️ **RABBITMQ_ERLANG_COOKIE** - 改为唯一随机值

**生成随机值的命令：**
```bash
openssl rand -base64 50  # 用于 SECRET_KEY
openssl rand -base64 32  # 用于密码
```

---

## 📦 包含的文件

### 配置文件（必须）
- `.env` - 环境变量配置（需要修改）
- `docker-compose.yml` - Docker 服务编排（已优化）
- `docker-compose-inits.yml` - 初始化配置
- `taiga-gateway/taiga.conf` - Nginx 网关配置（已优化）

### 启动脚本
- `launch-taiga.sh` - 启动所有容器
- `taiga-manage.sh` - Django 管理命令

### 文档（中文）
- `START_HERE.md` - 本文档，快速导航
- `README_CN.md` - 中文项目说明
- `QUICK_START.md` - 快速部署指南
- `DEPLOYMENT.md` - 完整部署指南
- `DEPLOYMENT_CHECKLIST.md` - 部署检查清单
- `TROUBLESHOOTING.md` - 故障排查指南
- `CHANGES_SUMMARY.md` - 配置修改摘要
- `BAOTA_NGINX_CONFIG.txt` - Nginx 配置示例

---

## 🎯 推荐的阅读顺序

### 新手用户

1. **START_HERE.md**（本文档）← 您在这里
2. **QUICK_START.md**（快速开始）
3. **DEPLOYMENT_CHECKLIST.md**（检查清单）
4. **TROUBLESHOOTING.md**（遇到问题时查看）

### 有经验的用户

1. **CHANGES_SUMMARY.md**（了解修改内容）
2. 直接修改 `.env` 文件
3. 执行部署命令
4. **DEPLOYMENT_CHECKLIST.md**（验证部署）

---

## 🆘 需要帮助？

### 文档内找答案
- **部署问题** → [DEPLOYMENT.md](DEPLOYMENT.md)
- **配置问题** → [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)
- **故障问题** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **验证问题** → [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

### 官方资源
- **Taiga 官方文档**：https://docs.taiga.io/
- **Taiga 社区**：https://community.taiga.io/
- **GitHub Issues**：https://github.com/taigaio/taiga-docker/issues

### 查看日志
```bash
cd /www/wwwroot/taiga
docker-compose logs -f
```

---

## 📞 技术支持渠道

1. **阅读文档**（优先推荐）
   - 本项目包含完整的中文文档
   - 覆盖部署、配置、故障排查等所有场景

2. **查看日志**（自我排查）
   - 容器日志：`docker-compose logs`
   - Nginx 日志：宝塔面板查看
   - 系统日志：`journalctl -u docker`

3. **官方社区**（寻求帮助）
   - Taiga 社区论坛
   - GitHub Issues
   - 官方文档

---

## 🎉 准备好了吗？

现在您可以：

1. 🔧 **配置环境** - 修改 `.env` 文件
2. 📚 **选择文档** - 根据需求选择上述文档
3. 🚀 **开始部署** - 按照文档执行步骤
4. ✅ **验证部署** - 使用检查清单验证

---

## 💡 温馨提示

- ⏰ **首次部署预计耗时**：30-60 分钟
- 📝 **必读文档**：QUICK_START.md 或 DEPLOYMENT.md
- ✅ **部署后检查**：DEPLOYMENT_CHECKLIST.md
- 🔐 **安全第一**：务必修改所有默认密码

---

**祝您部署顺利！** 🎊

如有任何问题，请参考相应的文档或查看故障排查指南。

---

## 📝 版本信息

- **配置版本**：2024 生产环境优化版
- **适用场景**：宝塔面板 + 顶级域名 + HTTPS
- **文档语言**：简体中文
- **最后更新**：2024-11

---

<p align="center">
  <strong>开始您的 Taiga 之旅吧！</strong>
</p>
