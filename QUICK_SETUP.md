# 🚀 Quick Setup Guide - New Features

## What's New?

Your Taiga instance now has 3 powerful new features:

1. ✅ **Django Admin Export/Import** - Backup and migrate configurations
2. ✅ **Default Chinese Language** - All new users automatically use Chinese
3. ✅ **Custom Fields in Lists** - See custom fields on cards without clicking

---

## ⚡ Quick Start (5 minutes)

### Step 1: Run Setup Script
```bash
./scripts/setup_custom_fields.sh
```

### Step 2: Set All Users to Chinese
```bash
docker compose exec taiga-back python manage.py set_users_chinese
```

### Step 3: Restart Services
```bash
docker compose restart taiga-front taiga-back
```

### Step 4: Verify
1. Visit: `https://yourdomain.com/admin/`
2. Login with your admin account
3. You should see "Taiga Custom Auto-Assign" section

---

## 📋 Feature Usage

### Export Configuration
```
1. Go to: https://yourdomain.com/admin/
2. Click: "Export Configuration"
3. Select what to export
4. Download the file
```

### Import Configuration
```
1. Go to: https://yourdomain.com/admin/
2. Click: "Import Configuration"
3. Upload your export file
4. Review import report
```

### Batch Update User Language
```bash
# Update all users to Chinese
docker compose exec taiga-back python manage.py set_users_chinese

# Preview changes first (dry run)
docker compose exec taiga-back python manage.py set_users_chinese --dry-run

# Only update users without language set
docker compose exec taiga-back python manage.py set_users_chinese --only-unset
```

### Custom Fields Display
```
No action needed!
- Custom fields automatically appear on cards
- Works in Kanban, Backlog, and all list views
```

---

## 🎯 What You Get

### Before
- ❌ No easy way to export/import configurations
- ❌ Manual language setting for each user
- ❌ Must click each card to see custom fields

### After
- ✅ One-click export/import in Admin
- ✅ New users automatically use Chinese
- ✅ Custom fields visible on all cards

---

## 📁 Files Created

### Backend (Django)
```
taiga-custom/
├── admin.py              ← Admin interface for export/import
├── views.py              ← Export/import views
├── urls.py               ← URL routing
├── importers.py          ← Import logic
├── serializers.py        ← Enhanced API responses
├── signals.py            ← Updated with language setting
├── config.py             ← Updated with new settings
└── management/commands/
    └── set_users_chinese.py  ← Language batch update
```

### Frontend
```
taiga-front/
├── conf.json             ← Frontend configuration
├── custom-fields.js      ← Custom fields display logic
└── custom-fields.css     ← Styling
```

### Scripts
```
scripts/
└── setup_custom_fields.sh  ← Setup script
```

### Documentation
```
FEATURES_GUIDE.md         ← Complete feature documentation
QUICK_SETUP.md           ← This file
```

---

## 🔍 Verify Installation

### Check Backend
```bash
# Verify custom app is loaded
docker compose exec taiga-back python manage.py showmigrations | grep custom

# Check if language setting works
docker compose logs taiga-back | grep "language"

# Test management command
docker compose exec taiga-back python manage.py set_users_chinese --dry-run
```

### Check Frontend
```bash
# Verify files are mounted
docker compose exec taiga-front ls -la /usr/share/nginx/html/ | grep custom

# Should see:
# custom-fields.js
# custom-fields.css
# conf.json
```

### Check Admin Access
```
1. Visit: https://yourdomain.com/admin/
2. Login with superuser
3. Look for "Taiga Custom Auto-Assign" section
4. Try "Export Configuration"
```

---

## 🐛 Troubleshooting

### Can't see Export/Import in Admin
```bash
# Restart backend
docker compose restart taiga-back

# Wait 30 seconds, then check again
```

### Language not setting automatically
```bash
# Check environment variable
docker compose exec taiga-back env | grep DEFAULT_USER_LANGUAGE

# Should show: DEFAULT_USER_LANGUAGE=zh-Hans
# If not, restart:
docker compose restart taiga-back
```

### Custom fields not showing
```bash
# Clear browser cache
# Hard refresh: Ctrl+Shift+R

# Or restart frontend
docker compose restart taiga-front
```

### Import fails
```
Common causes:
- Duplicate usernames → Use "merge" mode
- Missing users → Import users first
- File format wrong → Use .json or .zip
```

---

## 📚 Learn More

For detailed documentation, see:
- **FEATURES_GUIDE.md** - Complete feature documentation
- **AUTO_ASSIGN_README.md** - Auto-assign feature details

---

## 🎉 You're All Set!

Your Taiga instance is now enhanced with:
- ✅ Easy backup and migration
- ✅ Automatic Chinese language
- ✅ Custom fields in list views

**Next Steps:**
1. Create a test user → Should automatically be Chinese
2. Try exporting your configuration
3. Open a project → See custom fields on cards

**Enjoy your enhanced Taiga! 🚀**
