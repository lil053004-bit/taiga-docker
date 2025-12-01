# Taiga Enhanced Features Guide

This guide covers the three major enhancements added to your Taiga installation:

1. **Django Admin Export/Import Configuration**
2. **Default Chinese Language for All Users**
3. **Custom Fields Display in List Views**

---

## 📦 Feature 1: Django Admin Export/Import

### Overview
Export and import Taiga configurations (projects, users, tasks, etc.) directly from the Django Admin interface.

### Access
1. Go to `https://yourdomain.com/admin/`
2. Login with your superuser account
3. Look for the "Taiga Custom Auto-Assign" section

### Export Configuration

**Steps:**
1. Click on "Export Configuration" in the admin menu
2. Select what to export:
   - ☑️ Projects
   - ☑️ Users
   - ☑️ Memberships
   - ☑️ User Stories
   - ☑️ Tasks
   - ☑️ Issues
   - ☑️ Custom Attributes
3. Choose format: JSON or ZIP
4. Click "Export"
5. Download the generated file

**Export File Structure:**
```json
{
  "export_date": "2025-12-01T10:30:00",
  "export_version": "1.0",
  "projects": [...],
  "users": [...],
  "memberships": [...],
  "userstories": [...],
  "tasks": [...],
  "issues": [...],
  "custom_attributes": {...}
}
```

### Import Configuration

**Steps:**
1. Click on "Import Configuration" in the admin menu
2. Upload your JSON or ZIP file
3. Choose import mode:
   - **Merge**: Update existing items, create new ones
   - **Skip**: Only create items that don't exist
4. Click "Import"
5. Review the import report

**Import Report Shows:**
- Users created/updated
- Projects created/updated
- Memberships created
- Any errors encountered

### Use Cases

**Scenario 1: Backup Configuration**
```bash
# Regular backups
1. Export all configuration monthly
2. Store in secure location
3. Use for disaster recovery
```

**Scenario 2: Clone Taiga Instance**
```bash
# From old instance
1. Export all configuration

# On new instance
2. Import the configuration file
3. All projects, users, and memberships are recreated
```

**Scenario 3: Migrate Between Servers**
```bash
1. Export from old server
2. Set up new Taiga instance
3. Import configuration
4. Verify data integrity
```

---

## 🇨🇳 Feature 2: Default Chinese Language

### Overview
Automatically set all new users' language to Chinese (zh-Hans) and batch update existing users.

### Automatic Setting for New Users

**How it works:**
- When a new user registers or is created
- Their language is automatically set to `zh-Hans` (Simplified Chinese)
- No manual action required

**Configuration:**
The default language is set in `docker-compose.yml`:
```yaml
environment:
  DEFAULT_USER_LANGUAGE: "zh-Hans"
```

### Batch Update Existing Users

**Command:**
```bash
docker compose exec taiga-back python manage.py set_users_chinese
```

**Options:**

1. **Update all users:**
```bash
docker compose exec taiga-back python manage.py set_users_chinese
```

2. **Update only users without language set:**
```bash
docker compose exec taiga-back python manage.py set_users_chinese --only-unset
```

3. **Preview changes (dry run):**
```bash
docker compose exec taiga-back python manage.py set_users_chinese --dry-run
```

4. **Set different language:**
```bash
docker compose exec taiga-back python manage.py set_users_chinese --lang=en
```

**Output Example:**
```
============================================================
Setting User Language to Chinese
============================================================

Mode: Update ALL users
Language: zh-Hans
Total users to update: 15

✓ User 'admin' (admin@example.com): en → zh-Hans
✓ User 'adsadmin' (lhweave@gmail.com): not set → zh-Hans
✓ User 'user1' (user1@example.com): en → zh-Hans
...

============================================================
Summary
============================================================
Total users processed: 15
✓ Successfully updated 15 users to zh-Hans
```

### Django Admin Language Management

**Bulk Actions in Admin:**
1. Go to `https://yourdomain.com/admin/users/user/`
2. Select users
3. Choose action:
   - "Set language to Chinese (简体中文)"
   - "Set language to English"
4. Click "Go"

**View Language Statistics:**
1. Go to Admin > Custom > Language Statistics
2. See distribution of languages across all users
3. Identify users without language set

---

## 🎨 Feature 3: Custom Fields Display in List Views

### Overview
Display custom fields directly on cards in Kanban, Backlog, and other list views without opening the detail page.

### Features

**Where Custom Fields Appear:**
- ✅ Kanban board cards
- ✅ Backlog items
- ✅ Sprint taskboard
- ✅ User Stories list
- ✅ Tasks list
- ✅ Issues list

### Configuration

**Frontend Configuration** (`taiga-front/conf.json`):
```json
{
  "customFields": {
    "showInList": true,
    "showInKanban": true,
    "showInBacklog": true,
    "maxFieldsToShow": 3,
    "layout": "compact"
  },
  "defaultLanguage": "zh-Hans"
}
```

**Options:**
- `showInList`: Enable/disable custom fields in lists
- `showInKanban`: Enable/disable in Kanban view
- `showInBacklog`: Enable/disable in Backlog
- `maxFieldsToShow`: Maximum number of fields to display (1-5)
- `layout`: Display style ("compact" or "detailed")

### Visual Appearance

**Before:**
```
┌─────────────────────────┐
│ User Story Title        │
│ #123                    │
└─────────────────────────┘
```

**After:**
```
┌─────────────────────────┐
│ User Story Title        │
│ #123                    │
│ ─────────────────────── │
│ PRIORITY: High          │
│ DUE DATE: 2025-12-15    │
│ ASSIGNED: adsadmin      │
└─────────────────────────┘
```

### Styling

**Color-Coded Borders:**
- User Stories: Blue left border
- Tasks: Orange left border
- Issues: Red left border

**Responsive Design:**
- Desktop: Full display
- Tablet: Compact view
- Mobile: Minimal display

### Customization

**To modify displayed fields**, edit `taiga-front/custom-fields.js`:

```javascript
// Change maximum fields shown
const maxFields = customFieldsConfig.maxFieldsToShow;

// Filter specific fields
if (key === 'priority' || key === 'due_date') {
    // Display logic
}
```

**To modify styles**, edit `taiga-front/custom-fields.css`:

```css
.custom-fields-display {
    background: #your-color;
    border-left: 3px solid #your-border-color;
}
```

---

## 🚀 Quick Start Guide

### Initial Setup

1. **Run setup script:**
```bash
./scripts/setup_custom_fields.sh
```

2. **Set all users to Chinese:**
```bash
docker compose exec taiga-back python manage.py set_users_chinese
```

3. **Restart services:**
```bash
docker compose restart taiga-front taiga-back
```

4. **Verify installation:**
- Visit `https://yourdomain.com/admin/`
- Check that export/import options are available
- Open a project and verify custom fields display

### Daily Usage

**Export Configuration (Weekly Backup):**
```bash
1. Admin > Export Configuration
2. Select all options
3. Download ZIP file
4. Store securely
```

**Add New User (Auto Chinese):**
```bash
# New users automatically get Chinese language
# No action needed!
```

**View Custom Fields:**
```bash
# Just open any Kanban/Backlog view
# Custom fields automatically appear on cards
```

---

## 🔧 Troubleshooting

### Export/Import Not Working

**Problem:** Can't see export/import options in admin

**Solution:**
```bash
# Restart backend
docker compose restart taiga-back

# Check logs
docker compose logs taiga-back | grep custom

# Verify custom app is loaded
docker compose exec taiga-back python manage.py showmigrations
```

### Language Not Setting Automatically

**Problem:** New users still have English

**Solution:**
```bash
# Check environment variable
docker compose exec taiga-back env | grep DEFAULT_USER_LANGUAGE

# Should output: DEFAULT_USER_LANGUAGE=zh-Hans

# If not set, check docker-compose.yml
# Then restart:
docker compose restart taiga-back
```

### Custom Fields Not Displaying

**Problem:** Custom fields don't appear on cards

**Solution:**
```bash
# Check frontend files exist
ls -la taiga-front/

# Should see:
# - conf.json
# - custom-fields.js
# - custom-fields.css

# Check volume mounts in docker-compose.yml
docker compose config | grep taiga-front -A 10

# Restart frontend
docker compose restart taiga-front

# Clear browser cache
# Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
```

### Import Fails with Errors

**Problem:** Import shows errors

**Common causes:**
1. **User conflicts:** Users with same username exist
   - Solution: Use "merge" mode instead of "skip"

2. **Project conflicts:** Projects with same slug exist
   - Solution: Rename projects or use merge mode

3. **Missing references:** Referenced users/projects don't exist
   - Solution: Import users and projects first, then other items

---

## 📊 Statistics and Monitoring

### View Language Distribution

**In Django Admin:**
```
Admin > Custom > Language Statistics

Shows:
- Total users: 50
- Chinese (zh-Hans): 45
- English (en): 3
- Not set: 2
```

### View Export History

**Check recent exports:**
```bash
# Exports are timestamped
# Example: taiga-export-20251201-153045.json

# Keep organized with naming:
taiga-export-backup-weekly-20251201.zip
taiga-export-migration-20251201.zip
```

---

## 🔐 Security Notes

### Export Files

**Important:**
- Export files may contain sensitive data
- Store securely (encrypted storage recommended)
- Don't commit to version control
- Limit access to admin users only

**Sensitive Data in Exports:**
- User emails
- Project descriptions
- Task details
- Custom field values

### Import Safety

**Best Practices:**
- Always backup before importing
- Test imports on staging first
- Review import reports carefully
- Use "merge" mode for existing data

---

## 📝 Summary

### What You Get

1. **Export/Import:** Easy configuration backup and migration
2. **Chinese Default:** All new users automatically use Chinese
3. **Custom Fields:** See important fields without clicking

### Key Commands

```bash
# Setup
./scripts/setup_custom_fields.sh

# Set language
docker compose exec taiga-back python manage.py set_users_chinese

# Restart
docker compose restart taiga-front taiga-back

# Admin
https://yourdomain.com/admin/
```

### Support

For issues or questions:
1. Check this guide
2. Review troubleshooting section
3. Check Docker logs: `docker compose logs`
4. Verify file structure matches documentation

---

**Enjoy your enhanced Taiga experience! 🎉**
