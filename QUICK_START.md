# Taiga 快速启动指南

## 快速部署（3步完成）

### 1️⃣ 重启服务
```bash
cd /www/kairuiads/project
docker compose down
docker compose up -d
```

### 2️⃣ 等待启动
```bash
sleep 30
docker compose ps
```

### 3️⃣ 初始化系统
```bash
bash initialize.sh
```

## 登录信息

- **网址**: https://kairui.lhwebs.com
- **用户名**: adsadmin
- **密码**: A52290120a
- **管理面板**: https://kairui.lhwebs.com/admin/

## 验证修复

### 检查401错误是否解决
```bash
# 应该返回 200 OK
curl -I https://kairui.lhwebs.com/api/v1/
```

### 检查nginx配置
```bash
# 应该看到3个 X-Forwarded-Proto 行
docker compose exec taiga-gateway cat /etc/nginx/conf.d/default.conf | grep X-Forwarded-Proto
```

### 查看服务状态
```bash
docker compose ps
```

### 查看日志
```bash
# 后端日志
docker compose logs taiga-back --tail 50

# 所有服务日志
docker compose logs --tail 20
```

## 常用命令

### 重启特定服务
```bash
docker compose restart taiga-gateway
docker compose restart taiga-back
```

### 查看环境变量
```bash
docker compose exec taiga-back env | grep -E "CSRF|ALLOWED|PUBLIC"
```

### 手动创建用户（如果初始化脚本失败）
```bash
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_superuser(
    username='adsadmin',
    email='lhweave@gmail.com',
    password='A52290120a'
)
user.lang = 'zh-Hans'
user.save()
print('✓ 管理员用户创建成功')
EOF
```

## 已修复的问题

✅ **401认证错误**
- 添加了 X-Forwarded-Proto 和 X-Forwarded-For 头
- Django现在能正确识别HTTPS请求
- CSRF保护正常工作

✅ **自动初始化问题**
- 移除了不稳定的自动初始化代码
- 提供了稳定的初始化脚本
- 避免竞态条件

✅ **用户注册控制**
- 禁用了公开注册
- 只有管理员可以创建用户
- 提高了系统安全性

## 新增功能

### 自动分配功能
当创建新的用户故事、任务或问题时，会自动分配给管理员用户 (adsadmin)

### 中文默认语言
所有新用户默认使用中文界面

### 自定义字段支持
支持在列表、看板和待办事项中显示自定义字段

## 故障排除

### 如果还是401错误

1. **重启网关服务**
```bash
docker compose restart taiga-gateway
```

2. **强制重新创建容器**
```bash
docker compose up -d --force-recreate taiga-gateway taiga-back
```

3. **清除浏览器缓存和Cookie**
- 按 Ctrl+Shift+Delete
- 清除所有缓存和Cookie
- 重新登录

### 如果无法登录

1. **重置管理员密码**
```bash
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='adsadmin')
user.set_password('A52290120a')
user.save()
print('✓ 密码已重置')
EOF
```

2. **检查用户状态**
```bash
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='adsadmin')
print(f'Active: {user.is_active}')
print(f'Staff: {user.is_staff}')
print(f'Superuser: {user.is_superuser}')
EOF
```

### 如果服务无法启动

1. **查看详细日志**
```bash
docker compose logs -f
```

2. **检查端口占用**
```bash
netstat -tlnp | grep 9090
```

3. **清理并重启**
```bash
docker compose down -v
docker compose up -d
sleep 30
bash initialize.sh
```

## 数据备份

### 备份数据库
```bash
docker compose exec taiga-db pg_dump -U taiga taiga > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 恢复数据库
```bash
cat backup_20241201_120000.sql | docker compose exec -T taiga-db psql -U taiga taiga
```

## 需要帮助？

详细文档请查看: `DEPLOYMENT_INSTRUCTIONS.md`

遇到问题请提供：
1. 错误截图
2. 日志输出 (`docker compose logs`)
3. 浏览器开发者工具的网络标签页截图
