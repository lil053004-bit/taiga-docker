# ⚡ Quick Start - Taiga Auto-Assign

## 🎯 What This Does
Automatically assigns all new tasks, user stories, and issues to **adsadmin** (lhweave@gmail.com)

---

## 🚀 Three Commands to Get Started

```bash
# 1. Setup (one time)
./scripts/setup_auto_assign.sh

# 2. Test it works
./scripts/test_auto_assign.sh

# 3. Done! Create a project to test
```

---

## ✅ What You Get

After setup:
- ✅ New projects automatically include **adsadmin** as member
- ✅ New user stories automatically assigned to **adsadmin**
- ✅ New tasks automatically assigned to **adsadmin**
- ✅ New issues automatically assigned to **adsadmin**

---

## 🔧 Useful Commands

```bash
# Add admin to all existing projects
./taiga-manage.sh add_admin_to_all_projects

# Fix any unassigned items
./taiga-manage.sh fix_unassigned_items

# View logs
tail -f logs/auto_assign.log

# Test status
./scripts/test_auto_assign.sh
```

---

## 📚 More Help

- **Quick Usage:** See `USAGE_GUIDE.md`
- **Full Docs:** See `AUTO_ASSIGN_README.md`
- **Setup Details:** See `docs/AUTO_ASSIGN_SETUP.md`
- **Troubleshooting:** See `docs/AUTO_ASSIGN_MAINTENANCE.md`

---

## 🆘 Problems?

```bash
# Run diagnostics
./scripts/test_auto_assign.sh

# Check logs
tail -50 logs/auto_assign.log

# Restart services
docker compose restart taiga-back taiga-async
```

---

**That's it! You're ready to go! 🎉**
