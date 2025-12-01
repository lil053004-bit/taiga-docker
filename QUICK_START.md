# Taiga 快速部署指南 / Quick Start Guide

## 一键部署（推荐） / One-Command Deployment (Recommended)

最简单的部署方式：

```bash
bash deploy.sh
```

就这么简单！脚本会自动完成所有步骤。

That's it! The script will handle everything automatically.

---

## 手动部署 / Manual Deployment

如果需要手动控制每个步骤 / If you need to control each step manually:

### 步骤 1: 停止现有服务 / Step 1: Stop Existing Services

```bash
docker compose down
```

### 步骤 2: 启动所有服务 / Step 2: Start All Services

```bash
docker compose up -d
```

### 步骤 3: 等待服务就绪 / Step 3: Wait for Services

```bash
sleep 30
```

### 步骤 4: 运行初始化 / Step 4: Run Initialization

```bash
bash initialize.sh
```

### 步骤 5: 验证部署（可选） / Step 5: Verify Deployment (Optional)

```bash
bash verify_custom_app.sh
bash scripts/verify_installation.sh
```

---

## 登录信息 / Login Credentials

- **URL**: https://kairui.lhwebs.com
- **用户名 / Username**: adsadmin
- **密码 / Password**: A52290120a
- **管理面板 / Admin Panel**: https://kairui.lhwebs.com/admin/

---

## 常用命令 / Useful Commands

### 查看服务状态 / Check Service Status
```bash
docker compose ps
```

### 查看日志 / View Logs
```bash
# 所有服务 / All services
docker compose logs -f

# 特定服务 / Specific service
docker compose logs -f taiga-back
docker compose logs -f taiga-front
docker compose logs -f taiga-gateway
```

### 重启服务 / Restart Services
```bash
# 所有服务 / All services
docker compose restart

# 特定服务 / Specific service
docker compose restart taiga-back
docker compose restart taiga-front
```

### 停止服务 / Stop Services
```bash
docker compose down
```

---

## 故障排除 / Troubleshooting

### 问题 1: 看到 401 错误 / Issue 1: Seeing 401 Errors

**解决方案 / Solution:**
```bash
# 验证 Nginx 配置 / Verify Nginx configuration
docker compose exec taiga-gateway nginx -t

# 检查代理头 / Check proxy headers
docker compose exec taiga-gateway grep -c "X-Forwarded-Proto" /etc/nginx/conf.d/default.conf
# 应该输出 4 / Should output: 4

# 重启网关 / Restart gateway
docker compose restart taiga-gateway
```

### 问题 2: JavaScript 错误 / Issue 2: JavaScript Errors

**解决方案 / Solution:**
1. 清除浏览器缓存 / Clear browser cache (Ctrl+Shift+Delete)
2. 使用无痕模式 / Use incognito/private mode
3. 强制刷新 / Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### 问题 3: 界面不是中文 / Issue 3: Interface Not in Chinese

**解决方案 / Solution:**
```bash
# 设置所有用户为中文 / Set all users to Chinese
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
updated = User.objects.all().update(lang='zh-Hans')
print(f'Updated {updated} users to Chinese')
EOF

# 重启服务 / Restart services
docker compose restart
```

### 问题 4: 无法连接数据库 / Issue 4: Cannot Connect to Database

**解决方案 / Solution:**
```bash
# 检查数据库状态 / Check database status
docker compose ps taiga-db

# 查看数据库日志 / View database logs
docker compose logs taiga-db

# 重启数据库 / Restart database
docker compose restart taiga-db

# 等待并重新初始化 / Wait and reinitialize
sleep 10
bash initialize.sh
```

### 问题 5: 自动分配功能不工作 / Issue 5: Auto-Assign Not Working

**解决方案 / Solution:**
```bash
# 1. 验证自定义应用是否加载 / Verify custom app is loaded
bash verify_custom_app.sh

# 2. 检查配置 / Check configuration
docker compose exec -T taiga-back python -c "
from django.conf import settings
print('Custom app loaded:', 'custom' in settings.INSTALLED_APPS)
print('Auto-assign enabled:', getattr(settings, 'AUTO_ASSIGN_ENABLED', False))
print('Admin username:', getattr(settings, 'AUTO_ASSIGN_ADMIN_USERNAME', 'not set'))
"

# 3. 如果应用未加载，重启服务 / If app not loaded, restart services
docker compose down
docker compose up -d
sleep 30
bash initialize.sh

# 4. 查看自定义应用日志 / Check custom app logs
tail -f logs/custom.log
```

### 问题 6: 无法保存项目详情 / Issue 6: Cannot Save Project Details

**解决方案 / Solution:**
```bash
# 1. 检查后端日志中的错误 / Check backend logs for errors
docker compose logs taiga-back --tail 100

# 2. 验证 CSRF 配置 / Verify CSRF configuration
docker compose exec -T taiga-back python -c "
import os
print('CSRF_TRUSTED_ORIGINS:', os.getenv('CSRF_TRUSTED_ORIGINS'))
print('ALLOWED_HOSTS:', os.getenv('ALLOWED_HOSTS'))
"

# 3. 清除浏览器缓存并重试 / Clear browser cache and retry
# 使用 Ctrl+Shift+Delete 或无痕模式

# 4. 检查 Nginx 配置 / Check Nginx configuration
docker compose exec taiga-gateway nginx -t
docker compose restart taiga-gateway
```

---

## 高级操作 / Advanced Operations

### 备份数据库 / Backup Database
```bash
docker compose exec taiga-db pg_dump -U taiga taiga > backup_$(date +%Y%m%d).sql
```

### 恢复数据库 / Restore Database
```bash
cat backup_20231201.sql | docker compose exec -T taiga-db psql -U taiga taiga
```

### 清理并重新部署 / Clean and Redeploy
```bash
# 警告：这将删除所有数据！/ Warning: This will delete all data!
docker compose down -v
bash deploy.sh
```

---

## 已修复的问题 / Fixed Issues

✅ **401 认证错误 / 401 Authentication Errors**
- 添加了所有必需的代理头 / Added all required proxy headers
- Django 正确识别 HTTPS 请求 / Django correctly identifies HTTPS requests
- CSRF 保护正常工作 / CSRF protection works correctly

✅ **JavaScript 错误 / JavaScript Errors**
- 简化前端配置避免冲突 / Simplified frontend config to avoid conflicts
- 确保 conf.json 正确加载 / Ensure conf.json loads correctly

✅ **默认语言设置 / Default Language Settings**
- 所有用户默认使用中文 / All users default to Chinese
- 前端界面默认显示中文 / Frontend interface defaults to Chinese
- 自动设置新用户语言 / Automatically set new user language

✅ **部署流程简化 / Deployment Process Simplified**
- 一键部署脚本 / One-command deployment script
- 自动验证和配置 / Automatic verification and configuration
- 清晰的错误提示 / Clear error messages

---

## 配置文件说明 / Configuration Files

- **`.env`**: 环境变量配置 / Environment variables
- **`docker-compose.yml`**: Docker 服务配置 / Docker services configuration
- **`taiga-gateway/taiga.conf`**: Nginx 反向代理配置 / Nginx reverse proxy config
- **`taiga-front/conf.json`**: 前端配置 / Frontend configuration
- **`initialize.sh`**: 初始化脚本 / Initialization script
- **`deploy.sh`**: 一键部署脚本 / One-command deployment script

---

## 重要安全提示 / Important Security Notes

1. **修改默认密码** / Change default password
   - 首次登录后立即修改管理员密码
   - Change admin password immediately after first login

2. **保护 .env 文件** / Protect .env file
   - 不要将 .env 文件提交到版本控制
   - Never commit .env file to version control

3. **使用强密码** / Use strong passwords
   - 数据库密码至少 16 个字符
   - Database password should be at least 16 characters

4. **定期备份** / Regular backups
   - 建议每天备份数据库
   - Recommend daily database backups

---

## 获取帮助 / Getting Help

如有问题，请检查：/ If you have issues, check:

1. Docker 日志 / Docker logs: `docker compose logs -f`
2. 服务状态 / Service status: `docker compose ps`
3. 配置验证 / Configuration verification: `bash scripts/verify_installation.sh`

详细文档 / Detailed documentation: `DEPLOYMENT_INSTRUCTIONS.md`

---

## 项目结构 / Project Structure

```
.
├── deploy.sh                    # 一键部署脚本 / One-command deployment
├── initialize.sh                # 初始化脚本 / Initialization script
├── docker-compose.yml           # Docker 配置 / Docker configuration
├── .env                         # 环境变量 / Environment variables
├── taiga-gateway/
│   └── taiga.conf              # Nginx 配置 / Nginx configuration
├── taiga-front/
│   ├── conf.json               # 前端配置 / Frontend config
│   ├── custom-fields.js        # 自定义字段 JS / Custom fields JS
│   └── custom-fields.css       # 自定义字段样式 / Custom fields CSS
├── taiga-custom/
│   ├── signals.py              # 自动分配逻辑 / Auto-assign logic
│   ├── settings.py             # Django 设置扩展 / Django settings extension
│   └── management/
│       └── commands/           # 管理命令 / Management commands
└── scripts/
    ├── verify_installation.sh  # 验证脚本 / Verification script
    └── test_auto_assign.sh     # 测试脚本 / Test script
```

---

**祝您使用愉快！/ Enjoy using Taiga!** 🎉
