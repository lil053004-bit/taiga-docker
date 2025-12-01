# 401错误修复 - 部署说明

## 修复内容

已完成以下关键修复来解决401认证错误：

### 1. 修复Nginx代理配置 ✓
在 `taiga-gateway/taiga.conf` 中为所有代理位置添加了必要的HTTP头：
- `X-Forwarded-Proto` - 让Django知道实际使用的是HTTPS协议
- `X-Forwarded-For` - 正确转发客户端IP地址

这些头对于CSRF保护正确工作至关重要。

### 2. 移除有问题的自动初始化 ✓
从 `taiga-custom/apps.py` 中移除了自动初始化代码，避免：
- 数据库未就绪时运行命令导致的竞态条件
- 重复初始化尝试
- 不可预测的启动行为

### 3. 添加用户注册控制 ✓
添加 `PUBLIC_REGISTER_ENABLED=False` 配置：
- 防止未授权的用户注册
- 提高系统安全性
- 保持用户管理的控制权

## 部署步骤

### 步骤1：停止所有服务
```bash
docker compose down
```

### 步骤2：启动所有服务
```bash
docker compose up -d
```

### 步骤3：等待服务完全启动
```bash
# 等待30秒让所有服务完全启动
sleep 30

# 检查服务状态
docker compose ps
```

### 步骤4：运行初始化命令（仅首次部署或重置后）
```bash
# 创建管理员用户
docker compose exec taiga-back python manage.py initialize_taiga

# 运行数据库迁移（如果需要）
docker compose exec taiga-back python manage.py migrate
```

### 步骤5：验证修复
```bash
# 1. 检查API端点
curl -I https://kairui.lhwebs.com/api/v1/

# 2. 检查后端日志
docker compose logs taiga-back --tail 50

# 3. 在浏览器中访问
# 打开: https://kairui.lhwebs.com
```

## 登录信息

- **用户名**: adsadmin
- **密码**: A52290120a
- **邮箱**: lhweave@gmail.com

## 验证清单

部署后，验证以下内容正常工作：

- [ ] 可以访问主页 (https://kairui.lhwebs.com)
- [ ] 可以登录系统
- [ ] API调用返回正常（不再是401错误）
- [ ] 可以创建新项目
- [ ] 可以创建用户故事/任务
- [ ] WebSocket事件正常工作
- [ ] 管理员面板可访问 (/admin/)

## 问题排查

### 如果仍然出现401错误：

1. **检查nginx配置是否生效**
```bash
docker compose exec taiga-gateway cat /etc/nginx/conf.d/default.conf | grep X-Forwarded-Proto
```
应该看到3个 `X-Forwarded-Proto` 行（Frontend、API、Admin各一个）

2. **检查环境变量**
```bash
docker compose exec taiga-back env | grep -E "CSRF_TRUSTED_ORIGINS|ALLOWED_HOSTS|PUBLIC_REGISTER"
```

3. **查看详细日志**
```bash
# 后端日志
docker compose logs taiga-back -f

# 网关日志
docker compose logs taiga-gateway -f

# 所有服务日志
docker compose logs -f
```

4. **重新构建容器（如果配置未生效）**
```bash
docker compose down
docker compose up -d --force-recreate taiga-gateway taiga-back taiga-async
```

### 如果初始化失败：

```bash
# 手动创建管理员用户
docker compose exec taiga-back python manage.py createsuperuser

# 检查数据库连接
docker compose exec taiga-back python manage.py dbshell
```

## 技术说明

### 为什么这些修复能解决401错误？

1. **X-Forwarded-Proto头**
   - Django的CSRF保护检查请求协议是否匹配 `CSRF_TRUSTED_ORIGINS`
   - 没有这个头，Django认为请求来自HTTP而不是HTTPS
   - 协议不匹配导致CSRF验证失败 → 401错误

2. **移除自动初始化**
   - 避免在Django应用就绪前运行数据库操作
   - 防止竞态条件和不可预测的行为
   - 使初始化过程更加明确和可控

3. **禁用公开注册**
   - 减少潜在的认证相关问题
   - 提高系统安全性
   - 简化用户管理

## 安全提示

- 系统已配置为HTTPS only
- CSRF保护已启用
- 公开注册已禁用
- 所有cookies通过HTTPS传输
- 主机头验证已配置

## 后续维护

### 添加新用户：
```bash
docker compose exec taiga-back python manage.py createsuperuser
```

### 备份数据库：
```bash
docker compose exec taiga-db pg_dump -U taiga taiga > backup_$(date +%Y%m%d).sql
```

### 查看自动分配日志：
```bash
docker compose logs taiga-back | grep "Auto-assign"
```

## 支持

如果遇到问题，请提供：
1. 错误信息截图
2. 相关日志（使用上述命令获取）
3. 浏览器开发者工具的网络选项卡截图（显示401错误的请求详情）
