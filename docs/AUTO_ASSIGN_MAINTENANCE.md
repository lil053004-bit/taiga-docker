# Taiga Auto-Assign Maintenance Guide

This guide covers maintenance, monitoring, and troubleshooting of the auto-assign system.

## 🔧 Regular Maintenance

### Daily Tasks

**Check Auto-Assign Status:**
```bash
# Quick verification
export ADMIN_PASSWORD='your-password'
python3 scripts/verify_auto_assign.py
```

**Review Logs:**
```bash
# Check for errors
grep -i error logs/auto_assign.log | tail -20

# Check recent activity
tail -50 logs/auto_assign.log
```

### Weekly Tasks

**Verify All Projects Have Admin:**
```bash
./taiga-manage.sh add_admin_to_all_projects --dry-run
```

**Fix Any Unassigned Items:**
```bash
./taiga-manage.sh fix_unassigned_items --dry-run
# If items found, run without --dry-run
./taiga-manage.sh fix_unassigned_items
```

### Monthly Tasks

**Clean Up Logs:**
```bash
# Archive old logs
mv logs/auto_assign.log logs/auto_assign.log.$(date +%Y%m%d)
touch logs/auto_assign.log
chmod 666 logs/auto_assign.log

# Keep only last 3 months
find logs/ -name "auto_assign.log.*" -mtime +90 -delete
```

**Verify Configuration:**
```bash
# Check all settings
cat .env | grep AUTO_ASSIGN

# Verify Docker configuration
docker compose config | grep -A 5 AUTO_ASSIGN
```

---

## 📊 Monitoring

### Key Metrics to Monitor

1. **Project Membership Coverage:**
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

2. **Unassigned Items Count:**
   ```bash
   docker exec -i taiga-db psql -U taiga -d taiga << EOF
   SELECT
     'User Stories' as type, COUNT(*) as unassigned
   FROM userstories_userstory
   WHERE assigned_to_id IS NULL
   UNION ALL
   SELECT 'Tasks', COUNT(*)
   FROM tasks_task
   WHERE assigned_to_id IS NULL
   UNION ALL
   SELECT 'Issues', COUNT(*)
   FROM issues_issue
   WHERE assigned_to_id IS NULL;
   EOF
   ```

3. **Recent Auto-Assignments:**
   ```bash
   grep "Auto-assigned" logs/auto_assign.log | tail -20
   ```

### Setting Up Monitoring Alerts

**Create a monitoring script:**

```bash
cat > scripts/monitor_auto_assign.sh << 'EOF'
#!/bin/bash

ALERT_EMAIL="your-email@example.com"
THRESHOLD=5

# Count unassigned items
UNASSIGNED=$(docker exec -i taiga-db psql -U taiga -d taiga -t << SQL
SELECT COUNT(*) FROM (
  SELECT id FROM userstories_userstory WHERE assigned_to_id IS NULL
  UNION ALL
  SELECT id FROM tasks_task WHERE assigned_to_id IS NULL
  UNION ALL
  SELECT id FROM issues_issue WHERE assigned_to_id IS NULL
) as all_unassigned;
SQL
)

if [ "$UNASSIGNED" -gt "$THRESHOLD" ]; then
  echo "Warning: $UNASSIGNED unassigned items found" | \
    mail -s "Taiga Auto-Assign Alert" $ALERT_EMAIL
fi
EOF

chmod +x scripts/monitor_auto_assign.sh
```

**Add to crontab:**
```bash
# Run every hour
0 * * * * /path/to/taiga/scripts/monitor_auto_assign.sh
```

---

## 🐛 Troubleshooting Guide

### Problem: New Projects Not Getting Admin

**Diagnosis:**
```bash
# 1. Check if signals are loaded
docker compose logs taiga-back | grep "signals loaded"

# 2. Check AUTO_ASSIGN_ENABLED
docker compose exec taiga-back env | grep AUTO_ASSIGN

# 3. Check custom module is mounted
docker compose exec taiga-back ls -la /taiga-back/custom/
```

**Solutions:**

1. **Verify configuration:**
   ```bash
   grep AUTO_ASSIGN .env
   ```

2. **Restart services:**
   ```bash
   docker compose restart taiga-back taiga-async
   ```

3. **Check logs for errors:**
   ```bash
   docker compose logs taiga-back | grep -i error
   ```

4. **Manually add admin:**
   ```bash
   ./taiga-manage.sh add_admin_to_all_projects
   ```

### Problem: Items Not Being Auto-Assigned

**Diagnosis:**
```bash
# 1. Verify admin is project member
docker exec -i taiga-db psql -U taiga -d taiga << EOF
SELECT p.name, m.id as membership_id
FROM projects_project p
LEFT JOIN projects_membership m ON p.id = m.project_id
  AND m.user_id = (SELECT id FROM users_user WHERE username = 'adsadmin')
WHERE m.id IS NULL;
EOF

# 2. Check signal logs
grep "auto-assign" logs/auto_assign.log -i | tail -20
```

**Solutions:**

1. **Add admin to project:**
   ```bash
   ./taiga-manage.sh add_admin_to_all_projects
   ```

2. **Fix existing unassigned items:**
   ```bash
   ./taiga-manage.sh fix_unassigned_items
   ```

3. **Check if items were created via bulk import:**
   - Bulk imports may bypass signals
   - Run fix_unassigned_items after imports

### Problem: Permission Errors in Logs

**Error:** "Permission denied: '/taiga-back/logs/auto_assign.log'"

**Solution:**
```bash
# Fix log directory permissions
chmod 777 logs/
touch logs/auto_assign.log
chmod 666 logs/auto_assign.log

# Restart services
docker compose restart taiga-back taiga-async
```

### Problem: Signal Handlers Not Working

**Diagnosis:**
```bash
# Check if custom app is loaded
docker compose exec taiga-back python manage.py shell << EOF
import sys
print('custom' in sys.modules)
EOF
```

**Solution:**
```bash
# 1. Verify config.py is mounted
docker compose exec taiga-back cat /taiga-back/settings/config.py

# 2. Check for Python errors
docker compose logs taiga-back | grep -i "custom\|signal"

# 3. Recreate containers
docker compose down
docker compose up -d
```

### Problem: Database Connection Errors

**Error:** "could not connect to server"

**Solution:**
```bash
# 1. Check database is running
docker compose ps taiga-db

# 2. Test connection
docker exec -it taiga-db psql -U taiga -d taiga -c "SELECT 1;"

# 3. Restart database
docker compose restart taiga-db
sleep 10
docker compose restart taiga-back taiga-async
```

---

## 🔄 Updating and Upgrading

### Updating Taiga Version

When upgrading Taiga:

1. **Backup custom files:**
   ```bash
   tar -czf backup-auto-assign-$(date +%Y%m%d).tar.gz \
     taiga-custom/ scripts/ .env docs/AUTO_ASSIGN*.md
   ```

2. **Update Taiga:**
   ```bash
   docker compose pull
   ```

3. **Verify mounts still work:**
   ```bash
   docker compose config | grep -A 10 taiga-custom
   ```

4. **Restart and test:**
   ```bash
   docker compose up -d
   sleep 30
   ./taiga-manage.sh add_admin_to_all_projects --dry-run
   ```

### Modifying Auto-Assign Logic

To change which items get auto-assigned:

1. **Edit signal handlers:**
   ```bash
   nano taiga-custom/signals.py
   ```

2. **Modify the conditions:**
   ```python
   # Example: Only auto-assign high priority items
   @receiver(post_save, sender='userstories.UserStory')
   def auto_assign_user_story(sender, instance, created, **kwargs):
       if created and not instance.assigned_to:
           if instance.priority and instance.priority.name == 'High':
               # ... assign logic
   ```

3. **Restart services:**
   ```bash
   docker compose restart taiga-back taiga-async
   ```

---

## 🔒 Security Considerations

### Protecting Admin Credentials

Never commit passwords to git:

```bash
# Add to .gitignore
echo "scripts/.env.local" >> .gitignore

# Use separate file for passwords
cat > scripts/.env.local << EOF
export ADMIN_PASSWORD='your-secure-password'
EOF
chmod 600 scripts/.env.local

# Source when needed
source scripts/.env.local
python3 scripts/auto_assign_admin.py
```

### Audit Auto-Assignments

Create audit trail:

```bash
# Log all assignments
docker exec -i taiga-db psql -U taiga -d taiga << EOF
SELECT
  'User Story' as type,
  us.subject,
  u.username as assigned_to,
  us.created_date
FROM userstories_userstory us
JOIN users_user u ON us.assigned_to_id = u.id
WHERE us.created_date > NOW() - INTERVAL '7 days'
  AND u.username = 'adsadmin'
ORDER BY us.created_date DESC
LIMIT 50;
EOF
```

---

## 📈 Performance Optimization

### For Large Installations

If you have hundreds of projects:

1. **Batch operations:**
   ```bash
   # Process in chunks
   ./taiga-manage.sh add_admin_to_all_projects
   ```

2. **Use database script for bulk:**
   ```bash
   # Faster for initial setup
   docker exec -i taiga-db psql -U taiga -d taiga < scripts/batch_add_admin.sql
   ```

3. **Monitor resource usage:**
   ```bash
   docker stats taiga-back
   ```

### Optimize Signal Performance

If signals are slow:

```python
# In signals.py, add caching
from django.core.cache import cache

def get_admin_user():
    admin = cache.get('auto_assign_admin_user')
    if not admin:
        admin = User.objects.filter(username=ADMIN_USERNAME).first()
        cache.set('auto_assign_admin_user', admin, 3600)  # Cache 1 hour
    return admin
```

---

## 🎯 Best Practices

1. **Always test with --dry-run first**
2. **Monitor logs regularly**
3. **Keep backups of configuration**
4. **Document any customizations**
5. **Test after Taiga updates**
6. **Use verification script before production changes**

---

## 📞 Getting Help

If you need assistance:

1. **Check logs first:**
   ```bash
   tail -100 logs/auto_assign.log
   docker compose logs taiga-back | tail -100
   ```

2. **Run diagnostics:**
   ```bash
   ./scripts/verify_auto_assign.py
   ```

3. **Gather information:**
   - Taiga version: `docker compose images taiga-back`
   - Error messages from logs
   - Steps to reproduce the issue
   - Configuration (without passwords)

---

## 🔄 Rollback Procedure

To disable auto-assign completely:

1. **Disable in .env:**
   ```bash
   sed -i 's/AUTO_ASSIGN_ENABLED=True/AUTO_ASSIGN_ENABLED=False/' .env
   ```

2. **Restart services:**
   ```bash
   docker compose restart taiga-back taiga-async
   ```

3. **Or remove custom configuration:**
   ```bash
   # Comment out in docker-compose.yml
   # - ./taiga-custom/config.py:/taiga-back/settings/config.py

   docker compose restart taiga-back taiga-async
   ```

---

## 📚 Additional Resources

- [Taiga API Documentation](https://docs.taiga.io/api.html)
- [Django Signals Documentation](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
