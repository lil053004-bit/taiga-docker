# Taiga Auto-Assign Setup Guide

This guide explains how to set up and use the automatic assignment system for Taiga.

## 📋 Overview

The auto-assign system automatically:
- Adds the admin user to all new projects as a member
- Assigns new user stories to the admin user
- Assigns new tasks to the admin user
- Assigns new issues to the admin user

**Admin Account:**
- Username: `adsadmin`
- Email: `lhweave@gmail.com`

---

## 🚀 Quick Start

### Step 1: Run the Setup Script

```bash
cd /path/to/your/taiga
chmod +x scripts/setup_auto_assign.sh
./scripts/setup_auto_assign.sh
```

This script will:
1. Check your configuration
2. Restart Taiga services with the new settings
3. Add the admin user to all existing projects

### Step 2: Verify Installation

```bash
export ADMIN_PASSWORD='your-admin-password'
python3 scripts/verify_auto_assign.py
```

### Step 3: Test the System

1. **Test Project Membership:**
   - Create a new project
   - Check if `adsadmin` is automatically added as a member
   - Check project settings → Members

2. **Test Auto-Assignment:**
   - Create a new user story
   - Check if it's automatically assigned to `adsadmin`
   - Repeat for tasks and issues

---

## ⚙️ Configuration

All settings are in the `.env` file:

```bash
# Auto-assign settings
AUTO_ASSIGN_ADMIN_USERNAME=adsadmin
AUTO_ASSIGN_ADMIN_EMAIL=lhweave@gmail.com
AUTO_ASSIGN_ENABLED=True
```

### Changing the Admin User

1. Edit `.env`:
   ```bash
   AUTO_ASSIGN_ADMIN_USERNAME=your-username
   AUTO_ASSIGN_ADMIN_EMAIL=your-email@example.com
   ```

2. Restart services:
   ```bash
   docker compose restart taiga-back taiga-async
   ```

### Disabling Auto-Assign

Set in `.env`:
```bash
AUTO_ASSIGN_ENABLED=False
```

Then restart:
```bash
docker compose restart taiga-back taiga-async
```

---

## 🔧 Management Commands

### Add Admin to All Projects

Manually add the admin user to all existing projects:

```bash
./taiga-manage.sh add_admin_to_all_projects

# With options:
./taiga-manage.sh add_admin_to_all_projects --username=adsadmin
./taiga-manage.sh add_admin_to_all_projects --dry-run  # Preview changes
```

### Fix Unassigned Items

Assign all unassigned user stories, tasks, and issues to admin:

```bash
./taiga-manage.sh fix_unassigned_items

# With options:
./taiga-manage.sh fix_unassigned_items --username=adsadmin
./taiga-manage.sh fix_unassigned_items --type=userstories  # Only user stories
./taiga-manage.sh fix_unassigned_items --type=tasks        # Only tasks
./taiga-manage.sh fix_unassigned_items --type=issues       # Only issues
./taiga-manage.sh fix_unassigned_items --dry-run          # Preview changes
```

---

## 📝 Using the API Script

For batch operations using the Taiga API:

```bash
cd scripts

# Install dependencies
pip3 install -r requirements.txt

# Set your admin password
export ADMIN_PASSWORD='your-password'
export TAIGA_URL='https://yourdomain.com'

# Run the script
python3 auto_assign_admin.py
```

---

## 🗄️ Using the Database Script

For direct database operations (fastest for large datasets):

```bash
# Copy SQL to container
docker cp scripts/batch_add_admin.sql taiga-db:/tmp/

# Execute SQL
docker exec -it taiga-db psql -U taiga -d taiga -f /tmp/batch_add_admin.sql

# Or in one command:
docker exec -i taiga-db psql -U taiga -d taiga < scripts/batch_add_admin.sql
```

---

## 📊 Viewing Logs

Check the auto-assign logs:

```bash
# View recent logs
tail -f logs/auto_assign.log

# View Docker logs
docker compose logs -f taiga-back | grep custom
```

---

## 🔍 Troubleshooting

### Admin Not Being Added to New Projects

1. Check if auto-assign is enabled:
   ```bash
   grep AUTO_ASSIGN_ENABLED .env
   ```

2. Check Docker logs:
   ```bash
   docker compose logs taiga-back | grep -i "auto"
   ```

3. Verify signals are loaded:
   ```bash
   docker compose logs taiga-back | grep "signals loaded"
   ```

### Items Not Being Auto-Assigned

1. **Check if admin is a project member:**
   - The admin must be a member of the project
   - Run: `./taiga-manage.sh add_admin_to_all_projects`

2. **Check item creation method:**
   - Auto-assign works when items are created via the API/UI
   - Bulk imports may need manual assignment

3. **Check logs for errors:**
   ```bash
   tail -100 logs/auto_assign.log
   ```

### Services Won't Start

1. Check Docker logs:
   ```bash
   docker compose logs taiga-back
   ```

2. Verify volume mounts:
   ```bash
   docker compose config | grep -A 10 volumes
   ```

3. Check file permissions:
   ```bash
   ls -la taiga-custom/
   ls -la logs/
   ```

---

## 🔄 Updating the System

After Taiga updates:

1. Verify custom files are still mounted:
   ```bash
   docker compose exec taiga-back ls -la /taiga-back/custom/
   ```

2. Re-run setup if needed:
   ```bash
   ./scripts/setup_auto_assign.sh
   ```

---

## 📚 Advanced Usage

### Running Commands Inside Container

```bash
# Access container shell
docker compose exec taiga-back bash

# Run management command
python manage.py add_admin_to_all_projects

# Check Python path
python -c "import custom; print(custom.__file__)"
```

### Checking Signal Registration

```bash
docker compose exec taiga-back python manage.py shell << EOF
from django.db.models import signals
from taiga.projects.models import Project
print([s for s in signals.post_save.receivers if 'custom' in str(s)])
EOF
```

---

## 🆘 Support

If you encounter issues:

1. Check logs: `tail -f logs/auto_assign.log`
2. Verify configuration: `cat .env | grep AUTO_ASSIGN`
3. Test manually: `./taiga-manage.sh add_admin_to_all_projects --dry-run`
4. Review Docker logs: `docker compose logs taiga-back`

---

## 📄 Files Overview

```
project/
├── .env                              # Configuration
├── docker-compose.yml                # Modified with custom volumes
├── scripts/
│   ├── auto_assign_admin.py         # API batch script
│   ├── batch_add_admin.sql          # Database script
│   ├── setup_auto_assign.sh         # Setup script
│   ├── verify_auto_assign.py        # Verification script
│   └── requirements.txt             # Python dependencies
├── taiga-custom/
│   ├── __init__.py                  # Package init
│   ├── apps.py                      # Django app config
│   ├── config.py                    # Django settings
│   ├── signals.py                   # Signal handlers
│   └── management/commands/         # Django commands
└── logs/
    └── auto_assign.log              # Operation logs
```
