# 🚀 Taiga Auto-Assign - Quick Usage Guide

## 📖 What This Does

This auto-assign system ensures that:
1. **Admin user `adsadmin` is automatically added to all projects**
2. **All new user stories are automatically assigned to admin**
3. **All new tasks are automatically assigned to admin**
4. **All new issues are automatically assigned to admin**

## ⚡ Quick Start (3 Steps)

### Step 1: Run Setup

```bash
cd /path/to/your/taiga
./scripts/setup_auto_assign.sh
```

This will:
- ✅ Configure everything automatically
- ✅ Restart Taiga with new settings
- ✅ Add admin to all existing projects

### Step 2: Test the System

```bash
./scripts/test_auto_assign.sh
```

This checks:
- ✅ Services running
- ✅ Custom code mounted
- ✅ Admin user exists
- ✅ Configuration correct

### Step 3: Verify It's Working

1. **Go to your Taiga instance**
2. **Create a new project**
3. **Check Settings → Members** - `adsadmin` should be there automatically!
4. **Create a user story** - Should be assigned to `adsadmin` automatically!

---

## 🎯 Common Tasks

### Add Admin to All Existing Projects

```bash
# See what will be done (dry run)
./taiga-manage.sh add_admin_to_all_projects --dry-run

# Actually do it
./taiga-manage.sh add_admin_to_all_projects
```

### Fix Unassigned Items

```bash
# Fix all unassigned user stories, tasks, and issues
./taiga-manage.sh fix_unassigned_items

# Fix only specific type
./taiga-manage.sh fix_unassigned_items --type=userstories
./taiga-manage.sh fix_unassigned_items --type=tasks
./taiga-manage.sh fix_unassigned_items --type=issues
```

### Check Status

```bash
# Run comprehensive tests
./scripts/test_auto_assign.sh

# Or verify via API
export ADMIN_PASSWORD='your-password'
python3 scripts/verify_auto_assign.py
```

### View Logs

```bash
# Watch logs in real-time
tail -f logs/auto_assign.log

# Check for errors
grep ERROR logs/auto_assign.log

# See recent assignments
grep "Auto-assigned" logs/auto_assign.log | tail -20
```

---

## 🛠️ Troubleshooting

### Problem: Admin Not in New Projects

**Quick Fix:**
```bash
# 1. Check configuration
cat .env | grep AUTO_ASSIGN

# 2. Restart services
docker compose restart taiga-back taiga-async

# 3. Add manually if needed
./taiga-manage.sh add_admin_to_all_projects
```

### Problem: Items Not Auto-Assigned

**Quick Fix:**
```bash
# 1. Ensure admin is project member
./taiga-manage.sh add_admin_to_all_projects

# 2. Fix existing unassigned items
./taiga-manage.sh fix_unassigned_items
```

### Problem: Not Sure if It's Working

**Quick Fix:**
```bash
# Run the test script
./scripts/test_auto_assign.sh
```

---

## 📊 Check Your System

### How many projects have admin as member?

```bash
docker exec -i taiga-db psql -U taiga -d taiga << EOF
SELECT
  COUNT(DISTINCT p.id) as total_projects,
  COUNT(DISTINCT m.project_id) as projects_with_admin
FROM projects_project p
LEFT JOIN projects_membership m ON p.id = m.project_id
WHERE m.user_id = (SELECT id FROM users_user WHERE username = 'adsadmin');
EOF
```

### How many unassigned items?

```bash
docker exec -i taiga-db psql -U taiga -d taiga << EOF
SELECT
  'User Stories' as type, COUNT(*) as unassigned
FROM userstories_userstory WHERE assigned_to_id IS NULL
UNION ALL
SELECT 'Tasks', COUNT(*) FROM tasks_task WHERE assigned_to_id IS NULL
UNION ALL
SELECT 'Issues', COUNT(*) FROM issues_issue WHERE assigned_to_id IS NULL;
EOF
```

---

## ⚙️ Configuration

Everything is in `.env`:

```bash
# Edit these values
AUTO_ASSIGN_ADMIN_USERNAME=adsadmin
AUTO_ASSIGN_ADMIN_EMAIL=lhweave@gmail.com
AUTO_ASSIGN_ENABLED=True
```

After changing, restart:
```bash
docker compose restart taiga-back taiga-async
```

### Disable Auto-Assign

```bash
# In .env, change to:
AUTO_ASSIGN_ENABLED=False

# Then restart
docker compose restart taiga-back taiga-async
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `scripts/setup_auto_assign.sh` | One-click setup |
| `scripts/test_auto_assign.sh` | Test if working |
| `scripts/verify_auto_assign.py` | API verification |
| `taiga-manage.sh` | Run Django commands |
| `logs/auto_assign.log` | Operation logs |
| `.env` | Configuration |
| `AUTO_ASSIGN_README.md` | Full documentation |

---

## 🔄 Regular Maintenance

### Weekly Check

```bash
# Run test
./scripts/test_auto_assign.sh

# Check for unassigned items
./taiga-manage.sh fix_unassigned_items --dry-run
```

### Monthly Cleanup

```bash
# Archive old logs
mv logs/auto_assign.log logs/auto_assign.log.backup
touch logs/auto_assign.log
chmod 666 logs/auto_assign.log
```

---

## 💡 Pro Tips

1. **Always use --dry-run first** to preview changes
2. **Check logs regularly** for any issues
3. **Run test_auto_assign.sh** after Taiga updates
4. **Keep .env backed up** but never commit passwords

---

## 📚 More Help

- **Setup Details:** See `docs/AUTO_ASSIGN_SETUP.md`
- **Maintenance:** See `docs/AUTO_ASSIGN_MAINTENANCE.md`
- **Full Documentation:** See `AUTO_ASSIGN_README.md`

---

## 🆘 Emergency Commands

### Everything is broken, start over:

```bash
# 1. Stop services
docker compose down

# 2. Re-run setup
./scripts/setup_auto_assign.sh

# 3. Test
./scripts/test_auto_assign.sh
```

### Need to disable immediately:

```bash
# Quick disable
docker compose exec taiga-back sed -i 's/AUTO_ASSIGN_ENABLED=True/AUTO_ASSIGN_ENABLED=False/' /taiga-back/settings/config.py
docker compose restart taiga-back taiga-async
```

---

## ✅ Success Checklist

- [ ] Ran `./scripts/setup_auto_assign.sh`
- [ ] Ran `./scripts/test_auto_assign.sh` - all tests pass
- [ ] Created test project - admin added automatically
- [ ] Created test user story - assigned to admin automatically
- [ ] Checked logs - no errors
- [ ] All existing projects have admin as member

**If all checked, you're good to go! 🎉**

---

**Quick Reference Card**

```bash
# Setup
./scripts/setup_auto_assign.sh

# Test
./scripts/test_auto_assign.sh

# Add admin to all projects
./taiga-manage.sh add_admin_to_all_projects

# Fix unassigned items
./taiga-manage.sh fix_unassigned_items

# View logs
tail -f logs/auto_assign.log

# Restart services
docker compose restart taiga-back taiga-async
```

---

**Admin:** adsadmin (lhweave@gmail.com)
**Status:** Ready to use ✅
