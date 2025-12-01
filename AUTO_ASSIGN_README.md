# 🎯 Taiga Auto-Assign System

Automatically assign tasks, user stories, and issues to the admin user in Taiga.

## ✨ Features

- ✅ **Auto-add admin to new projects** - Admin becomes a member of every new project
- ✅ **Auto-assign user stories** - New user stories automatically assigned to admin
- ✅ **Auto-assign tasks** - New tasks automatically assigned to admin
- ✅ **Auto-assign issues** - New issues automatically assigned to admin
- ✅ **Batch processing** - Add admin to all existing projects at once
- ✅ **Fix unassigned items** - Retroactively assign existing unassigned items

## 📋 Configuration

**Admin Account:**
- Username: `adsadmin`
- Email: `lhweave@gmail.com`

**Settings in `.env`:**
```bash
AUTO_ASSIGN_ADMIN_USERNAME=adsadmin
AUTO_ASSIGN_ADMIN_EMAIL=lhweave@gmail.com
AUTO_ASSIGN_ENABLED=True
```

## 🚀 Quick Start

### 1. Run Setup Script

```bash
chmod +x scripts/setup_auto_assign.sh
./scripts/setup_auto_assign.sh
```

This will:
- Configure Docker with custom code
- Restart services
- Add admin to all existing projects

### 2. Verify Installation

```bash
export ADMIN_PASSWORD='your-password'
python3 scripts/verify_auto_assign.py
```

### 3. Test the System

1. **Create a new project** → Admin should be automatically added as member
2. **Create a user story** → Should be automatically assigned to admin
3. **Create a task** → Should be automatically assigned to admin
4. **Create an issue** → Should be automatically assigned to admin

## 🔧 Management Commands

### Add Admin to All Projects

```bash
# Preview what will be done
./taiga-manage.sh add_admin_to_all_projects --dry-run

# Actually add admin to all projects
./taiga-manage.sh add_admin_to_all_projects
```

### Fix Unassigned Items

```bash
# Fix all unassigned items
./taiga-manage.sh fix_unassigned_items

# Fix only user stories
./taiga-manage.sh fix_unassigned_items --type=userstories

# Preview changes
./taiga-manage.sh fix_unassigned_items --dry-run
```

## 📁 File Structure

```
project/
├── .env                                    # Configuration
├── docker-compose.yml                      # Modified for custom code
├── AUTO_ASSIGN_README.md                   # This file
│
├── scripts/
│   ├── auto_assign_admin.py               # API batch script
│   ├── batch_add_admin.sql                # Database batch script
│   ├── setup_auto_assign.sh               # One-click setup
│   ├── verify_auto_assign.py              # Verification tool
│   └── requirements.txt                   # Python dependencies
│
├── taiga-custom/
│   ├── __init__.py                        # Python package
│   ├── apps.py                            # Django app config
│   ├── config.py                          # Django settings
│   ├── signals.py                         # Auto-assign logic
│   └── management/commands/               # Django commands
│       ├── add_admin_to_all_projects.py
│       └── fix_unassigned_items.py
│
├── logs/
│   └── auto_assign.log                    # Operation logs
│
└── docs/
    ├── AUTO_ASSIGN_SETUP.md               # Detailed setup guide
    └── AUTO_ASSIGN_MAINTENANCE.md         # Maintenance guide
```

## 🔍 How It Works

### 1. Django Signals

The system uses Django signals to automatically respond to events:

- **Project Created** → Add admin as member with admin privileges
- **User Story Created** → Assign to admin (if not already assigned)
- **Task Created** → Assign to admin (if not already assigned)
- **Issue Created** → Assign to admin (if not already assigned)

### 2. Custom Django App

The `taiga-custom` directory is mounted into the Taiga container and loaded as a Django app, registering the signal handlers.

### 3. Docker Integration

Modified `docker-compose.yml` mounts:
- `./taiga-custom` → `/taiga-back/custom`
- `./taiga-custom/config.py` → `/taiga-back/settings/config.py`
- `./logs` → `/taiga-back/logs`

## 📊 Monitoring

### View Logs

```bash
# Real-time monitoring
tail -f logs/auto_assign.log

# Check for errors
grep ERROR logs/auto_assign.log

# Check recent assignments
grep "Auto-assigned" logs/auto_assign.log | tail -20
```

### Database Queries

```bash
# Check admin membership coverage
docker exec -i taiga-db psql -U taiga -d taiga << EOF
SELECT
  COUNT(DISTINCT p.id) as total_projects,
  COUNT(DISTINCT m.project_id) as projects_with_admin
FROM projects_project p
LEFT JOIN projects_membership m ON p.id = m.project_id
WHERE m.user_id = (SELECT id FROM users_user WHERE username = 'adsadmin');
EOF
```

```bash
# Count unassigned items
docker exec -i taiga-db psql -U taiga -d taiga << EOF
SELECT 'User Stories' as type, COUNT(*) as unassigned
FROM userstories_userstory WHERE assigned_to_id IS NULL
UNION ALL
SELECT 'Tasks', COUNT(*) FROM tasks_task WHERE assigned_to_id IS NULL
UNION ALL
SELECT 'Issues', COUNT(*) FROM issues_issue WHERE assigned_to_id IS NULL;
EOF
```

## 🛠️ Troubleshooting

### Admin Not Being Added to New Projects

1. Check if enabled: `grep AUTO_ASSIGN_ENABLED .env`
2. Check logs: `docker compose logs taiga-back | grep custom`
3. Restart services: `docker compose restart taiga-back`
4. Manually add: `./taiga-manage.sh add_admin_to_all_projects`

### Items Not Being Auto-Assigned

1. Ensure admin is project member
2. Check logs: `tail -50 logs/auto_assign.log`
3. Fix unassigned: `./taiga-manage.sh fix_unassigned_items`

### Signals Not Working

1. Verify mount: `docker compose exec taiga-back ls -la /taiga-back/custom/`
2. Check config: `docker compose exec taiga-back cat /taiga-back/settings/config.py`
3. Recreate containers: `docker compose down && docker compose up -d`

## ⚙️ Configuration Options

### Disable Auto-Assign

In `.env`:
```bash
AUTO_ASSIGN_ENABLED=False
```

Then restart:
```bash
docker compose restart taiga-back taiga-async
```

### Change Admin User

In `.env`:
```bash
AUTO_ASSIGN_ADMIN_USERNAME=new-admin
AUTO_ASSIGN_ADMIN_EMAIL=new-admin@example.com
```

Then restart and re-run setup.

## 🔄 Maintenance

### Daily
- Check logs for errors: `grep ERROR logs/auto_assign.log`

### Weekly
- Verify coverage: `python3 scripts/verify_auto_assign.py`
- Fix unassigned: `./taiga-manage.sh fix_unassigned_items --dry-run`

### Monthly
- Archive logs: `mv logs/auto_assign.log logs/auto_assign.log.$(date +%Y%m%d)`
- Verify configuration: `cat .env | grep AUTO_ASSIGN`

## 📚 Documentation

- **[Setup Guide](docs/AUTO_ASSIGN_SETUP.md)** - Detailed installation instructions
- **[Maintenance Guide](docs/AUTO_ASSIGN_MAINTENANCE.md)** - Monitoring and troubleshooting

## 🎯 Use Cases

### Solo Developer
Never manually assign tasks to yourself again!

### Team Lead
Automatically assign new items for triage before delegation.

### Project Manager
Keep admin visibility on all new work items.

## ⚠️ Important Notes

1. **Admin must exist** - User `adsadmin` must be created before auto-assign works
2. **Project membership required** - Admin must be a project member to be assigned items
3. **Respects existing assignments** - Won't override if item is already assigned
4. **Bulk imports** - Items created via bulk import may need manual fixing

## 🚀 Performance

- **Lightweight** - Minimal overhead, uses Django signals
- **Scalable** - Works efficiently with hundreds of projects
- **Reliable** - Database-backed with error handling

## 🔐 Security

- Never commit passwords to version control
- Use environment variables for sensitive data
- Audit auto-assignments regularly
- Keep logs secure and rotated

## 💡 Tips

1. **Use --dry-run first** to preview changes
2. **Monitor logs** regularly for issues
3. **Test after upgrades** to ensure compatibility
4. **Backup configuration** before making changes

## 🤝 Support

Having issues? Check:
1. Logs: `tail -100 logs/auto_assign.log`
2. Docker logs: `docker compose logs taiga-back`
3. Verification: `python3 scripts/verify_auto_assign.py`
4. Documentation: `docs/AUTO_ASSIGN_SETUP.md`

---

**Version:** 1.0
**Admin:** adsadmin (lhweave@gmail.com)
**Status:** Active ✅
