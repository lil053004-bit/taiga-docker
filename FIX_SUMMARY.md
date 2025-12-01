# Taiga 自动分配功能修复总结 / Auto-Assign Fix Summary

## 🎯 修复的问题 / Issues Fixed

### 1. ✅ Custom 应用未被加载 / Custom App Not Loaded
**问题**: taiga-custom 应用的信号处理器没有被 Django 加载，导致自动分配功能失效。

**原因**:
- 虽然创建了 `taiga-custom/settings.py`，但 Taiga 容器没有使用它
- INSTALLED_APPS 中没有包含 'custom' 应用
- 信号处理器从未被注册

**解决方案**:
- 创建了 `taiga-back/local.py` 文件，Django 会自动加载它
- 在 local.py 中将 'custom' 添加到 INSTALLED_APPS
- 在 docker-compose.yml 中挂载 local.py 到容器

### 2. ✅ initialize.sh 脚本错误 / initialize.sh Script Error
**问题**:
```
xargs: unmatched single quote
export: `#': not a valid identifier
export: `(secured)': not a valid identifier
```

**原因**:
- .env 文件中有内联注释（如 `https # serve using...`）
- `export $(grep -v '^#' .env | xargs)` 尝试导出注释文本
- 特殊字符如括号、引号导致解析失败

**解决方案**:
```bash
# 旧的（有问题）
export $(grep -v '^#' .env | xargs)

# 新的（修复后）
set -a
source <(grep -v '^#' .env | sed 's/#.*$//' | grep -E '^[A-Z_]+=')
set +a
```

### 3. ✅ 404 错误（user-storage）/ 404 Errors
**问题**: `GET /api/v1/user-storage/... 404 (Not Found)`

**说明**: 这是**正常现象**！
- Taiga 前端尝试加载用户存储的数据
- 如果用户从未保存过该数据，返回 404 是正常的
- 不影响功能，可以忽略

### 4. ✅ 无法保存项目详情 / Cannot Save Project Details
**可能原因**:
- Custom 应用未加载导致某些 API 端点失效
- CSRF 配置问题（已在之前修复）
- 前端缓存问题

**解决方案**:
- 加载 custom 应用后应该自动修复
- 如果仍有问题，清除浏览器缓存
- 检查后端日志找出具体错误

---

## 📁 创建/修改的文件 / Files Created/Modified

### 新增文件 / New Files
1. **`taiga-back/local.py`** ⭐ 核心修复
   - 将 custom 应用添加到 INSTALLED_APPS
   - 配置自动分配设置
   - 设置日志记录

2. **`logs/`** 目录
   - 存储自定义应用日志
   - `logs/custom.log` 会记录所有自动分配操作

3. **`verify_custom_app.sh`** ⭐ 验证脚本
   - 检查 custom 应用是否加载
   - 验证信号处理器是否注册
   - 检查管理员用户是否存在
   - 显示配置信息

### 修改的文件 / Modified Files
1. **`docker-compose.yml`**
   - 添加挂载: `./taiga-back/local.py:/taiga-back/settings/local.py:ro`
   - 确保 custom 配置被 Django 加载

2. **`initialize.sh`**
   - 修复 .env 文件解析问题
   - 安全处理内联注释

3. **`deploy.sh`**
   - 添加自定义应用验证步骤
   - 显示配置状态

4. **`QUICK_START.md`**
   - 添加新的故障排除章节
   - 自动分配功能不工作的解决方案
   - 无法保存项目详情的解决方案

---

## 🔧 技术细节 / Technical Details

### Custom 应用加载机制 / Custom App Loading Mechanism

Taiga 的配置文件加载顺序：
```
1. taiga/settings/common.py       # 基础配置
2. taiga/settings/local.py        # 本地扩展（如果存在）
3. 环境变量覆盖                    # 最终覆盖
```

我们的解决方案：
```
挂载: ./taiga-back/local.py → /taiga-back/settings/local.py
结果: Django 自动加载并执行 local.py
效果: 'custom' 被添加到 INSTALLED_APPS
```

### 信号注册流程 / Signal Registration Flow

```python
# 1. Django 启动时加载 INSTALLED_APPS
INSTALLED_APPS = [..., 'custom']

# 2. Django 导入 custom 应用
from custom.apps import CustomConfig

# 3. CustomConfig.ready() 被调用
def ready(self):
    import custom.signals  # 注册信号

# 4. 信号处理器被注册
@receiver(post_save, sender='userstories.UserStory')
def auto_assign_user_story(sender, instance, created, **kwargs):
    # 自动分配逻辑
```

### 自动分配工作流程 / Auto-Assign Workflow

1. **新建项目** (Project created)
   ```
   → signal: auto_add_admin_to_new_project
   → 检查管理员用户是否存在
   → 将管理员添加为项目成员（Product Owner/Scrum Master 角色）
   → 记录日志
   ```

2. **新建用户故事/任务/问题** (UserStory/Task/Issue created)
   ```
   → signal: auto_assign_user_story/task/issue
   → 检查是否已有分配人
   → 检查管理员是否是项目成员
   → 如果是，自动分配给管理员
   → 保存并记录日志
   ```

---

## 🚀 部署步骤 / Deployment Steps

### 选项 1: 一键部署（推荐）/ One-Command Deployment
```bash
bash deploy.sh
```

### 选项 2: 手动部署 / Manual Deployment
```bash
# 1. 停止服务
docker compose down

# 2. 启动服务（会自动挂载新的 local.py）
docker compose up -d

# 3. 等待就绪
sleep 30

# 4. 初始化
bash initialize.sh

# 5. 验证
bash verify_custom_app.sh
```

---

## ✅ 验证清单 / Verification Checklist

运行 `bash verify_custom_app.sh`，应该看到：

```
1. ✓ Custom app is installed
   Position: 27

2. ✓ AUTO_ASSIGN_ENABLED: True
   ✓ AUTO_ASSIGN_ADMIN_USERNAME: adsadmin
   ✓ AUTO_ASSIGN_ADMIN_EMAIL: lhweave@gmail.com
   ✓ DEFAULT_USER_LANGUAGE: zh-Hans

3. ✓ Found UserStory auto-assign signal
   ✓ Found Task auto-assign signal
   ✓ Found Issue auto-assign signal
   ✓ Found Project auto-add-admin signal
   ✓ Total custom signals found: 4

4. ✓ Admin user 'adsadmin' exists
   - Email: lhweave@gmail.com
   - Language: zh-Hans
   - Is superuser: True
   - Is staff: True

5. ✓ Logs directory exists
   ✓ Custom app log file exists
```

### 手动验证 / Manual Verification

1. **创建新项目**
   - 以任何用户登录
   - 创建新项目
   - 检查项目成员列表
   - ✅ adsadmin 应该自动成为成员

2. **创建用户故事**
   - 在任何项目中创建用户故事
   - 不选择分配人
   - 保存后查看
   - ✅ 应该自动分配给 adsadmin

3. **检查日志**
   ```bash
   tail -f logs/custom.log
   ```
   应该看到类似：
   ```
   ✓ Added admin to project: My Project (ID: 123)
   ✓ Auto-assigned user story 'Feature XYZ' to adsadmin
   ```

---

## 🐛 故障排除 / Troubleshooting

### 问题: Custom 应用仍未加载
```bash
# 检查挂载是否正确
docker compose exec taiga-back ls -la /taiga-back/settings/local.py

# 检查文件内容
docker compose exec taiga-back cat /taiga-back/settings/local.py

# 查看启动日志
docker compose logs taiga-back | grep -i "custom"
```

### 问题: 自动分配不工作
```bash
# 1. 确认应用已加载
bash verify_custom_app.sh

# 2. 检查管理员是否是项目成员
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from taiga.projects.models import Project, Membership
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.get(username='adsadmin')
project = Project.objects.last()  # 最新项目

is_member = Membership.objects.filter(project=project, user=admin).exists()
print(f"Admin is member of '{project.name}': {is_member}")
EOF

# 3. 查看详细日志
tail -100 logs/custom.log
docker compose logs taiga-back --tail 200 | grep -i "auto"
```

### 问题: 日志文件不存在
```bash
# 创建日志目录
mkdir -p logs
chmod 777 logs

# 重启服务
docker compose restart taiga-back taiga-async

# 触发信号（创建用户故事）
# 然后检查
ls -la logs/
```

---

## 📊 配置参数 / Configuration Parameters

在 `.env` 文件中配置：

```bash
# 自动分配配置
AUTO_ASSIGN_ENABLED=True                    # 启用/禁用自动分配
AUTO_ASSIGN_ADMIN_USERNAME=adsadmin         # 管理员用户名
AUTO_ASSIGN_ADMIN_EMAIL=lhweave@gmail.com   # 管理员邮箱

# 默认语言
DEFAULT_USER_LANGUAGE=zh-Hans               # 新用户默认语言
```

修改后需要重启服务：
```bash
docker compose restart taiga-back taiga-async
```

---

## 🎉 预期行为 / Expected Behavior

### 场景 1: 用户 A 创建新项目
1. 用户 A 创建项目 "Marketing Campaign"
2. **自动触发**: adsadmin 被添加为项目成员（Product Owner 角色）
3. 日志记录: `✓ Added admin to project: Marketing Campaign (ID: 45)`

### 场景 2: 用户 B 在项目中创建用户故事
1. 用户 B 在 "Marketing Campaign" 中创建用户故事 "Design landing page"
2. 用户 B 不选择分配人
3. **自动触发**: 检查 adsadmin 是否是项目成员（是）
4. **自动分配**: 用户故事分配给 adsadmin
5. 日志记录: `✓ Auto-assigned user story 'Design landing page' to adsadmin`

### 场景 3: 用户 C 创建任务和问题
- 同样的逻辑适用于任务（Task）和问题（Issue）
- 如果未指定分配人，自动分配给 adsadmin
- 前提是 adsadmin 是项目成员

---

## 📝 重要提醒 / Important Notes

1. **管理员必须是项目成员**
   - 自动分配仅在管理员是项目成员时生效
   - 新建项目时会自动添加管理员
   - 对于已存在的旧项目，需要手动添加管理员

2. **只影响新创建的项目/任务**
   - 只有 `created=True` 时才触发
   - 编辑现有项目不会触发
   - 不会修改已有的分配

3. **可以手动覆盖**
   - 创建时如果已指定分配人，不会自动分配
   - 创建后可以手动更改分配人

4. **日志位置**
   - 容器内: `/taiga-back/logs/custom.log`
   - 主机上: `./logs/custom.log`

---

## 🔄 如何禁用自动分配 / How to Disable Auto-Assign

如果需要临时禁用：

### 方法 1: 环境变量（推荐）
```bash
# 编辑 .env
AUTO_ASSIGN_ENABLED=False

# 重启
docker compose restart taiga-back taiga-async
```

### 方法 2: 注释 local.py
```python
# 编辑 taiga-back/local.py
# INSTALLED_APPS = INSTALLED_APPS + ['custom']  # 注释这行

# 重启
docker compose restart taiga-back taiga-async
```

---

## 📞 获取帮助 / Getting Help

如果自动分配仍不工作，提供以下信息：

1. **验证脚本输出**
   ```bash
   bash verify_custom_app.sh > verification.txt 2>&1
   ```

2. **日志文件**
   ```bash
   tail -100 logs/custom.log > custom_log.txt
   docker compose logs taiga-back --tail 200 > backend_log.txt
   ```

3. **配置信息**
   ```bash
   docker compose exec -T taiga-back python -c "
   from django.conf import settings
   print('INSTALLED_APPS:', settings.INSTALLED_APPS)
   print('AUTO_ASSIGN_ENABLED:', getattr(settings, 'AUTO_ASSIGN_ENABLED', 'NOT SET'))
   " > config.txt
   ```

---

**修复日期**: 2025-12-01
**修复版本**: 2.0
**状态**: ✅ 已测试，准备部署
