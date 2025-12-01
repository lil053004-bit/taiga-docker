#!/bin/bash

echo "=========================================="
echo "Taiga Custom App Verification"
echo "=========================================="
echo ""

echo "1. Checking if custom app is in INSTALLED_APPS..."
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from django.conf import settings
import sys

if 'custom' in settings.INSTALLED_APPS:
    print("✓ Custom app is installed")
    print(f"  Position: {settings.INSTALLED_APPS.index('custom')}")
else:
    print("✗ Custom app is NOT installed")
    sys.exit(1)
EOF

echo ""
echo "2. Checking auto-assign configuration..."
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from django.conf import settings

print(f"✓ AUTO_ASSIGN_ENABLED: {getattr(settings, 'AUTO_ASSIGN_ENABLED', 'NOT SET')}")
print(f"✓ AUTO_ASSIGN_ADMIN_USERNAME: {getattr(settings, 'AUTO_ASSIGN_ADMIN_USERNAME', 'NOT SET')}")
print(f"✓ AUTO_ASSIGN_ADMIN_EMAIL: {getattr(settings, 'AUTO_ASSIGN_ADMIN_EMAIL', 'NOT SET')}")
print(f"✓ DEFAULT_USER_LANGUAGE: {getattr(settings, 'DEFAULT_USER_LANGUAGE', 'NOT SET')}")
EOF

echo ""
echo "3. Checking if signals are registered..."
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from django.db.models import signals
import sys

# Check if our signal handlers are registered
signal_count = 0

# Check for userstories.UserStory signals
from taiga.projects.userstories.models import UserStory
handlers = signals.post_save._live_receivers(UserStory)
for handler in handlers:
    if 'auto_assign' in str(handler):
        print(f"✓ Found UserStory auto-assign signal: {handler}")
        signal_count += 1

# Check for tasks.Task signals
from taiga.projects.tasks.models import Task
handlers = signals.post_save._live_receivers(Task)
for handler in handlers:
    if 'auto_assign' in str(handler):
        print(f"✓ Found Task auto-assign signal: {handler}")
        signal_count += 1

# Check for issues.Issue signals
from taiga.projects.issues.models import Issue
handlers = signals.post_save._live_receivers(Issue)
for handler in handlers:
    if 'auto_assign' in str(handler):
        print(f"✓ Found Issue auto-assign signal: {handler}")
        signal_count += 1

# Check for projects.Project signals
from taiga.projects.models import Project
handlers = signals.post_save._live_receivers(Project)
for handler in handlers:
    if 'auto_add_admin' in str(handler):
        print(f"✓ Found Project auto-add-admin signal: {handler}")
        signal_count += 1

if signal_count > 0:
    print(f"\n✓ Total custom signals found: {signal_count}")
else:
    print("\n✗ No custom signals found - app may not be loaded properly")
    sys.exit(1)
EOF

echo ""
echo "4. Checking if admin user exists..."
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from django.contrib.auth import get_user_model
from django.conf import settings
import sys

User = get_user_model()
admin_username = getattr(settings, 'AUTO_ASSIGN_ADMIN_USERNAME', 'adsadmin')

try:
    admin = User.objects.get(username=admin_username)
    print(f"✓ Admin user '{admin_username}' exists")
    print(f"  - Email: {admin.email}")
    print(f"  - Language: {admin.lang}")
    print(f"  - Is superuser: {admin.is_superuser}")
    print(f"  - Is staff: {admin.is_staff}")
except User.DoesNotExist:
    print(f"✗ Admin user '{admin_username}' does NOT exist")
    print("  Run initialize.sh to create the admin user")
    sys.exit(1)
EOF

echo ""
echo "5. Checking logs directory..."
if [ -d "logs" ]; then
    echo "✓ Logs directory exists"
    if [ -f "logs/custom.log" ]; then
        echo "✓ Custom app log file exists"
        echo "  Last 5 lines:"
        tail -5 logs/custom.log | sed 's/^/    /'
    else
        echo "⚠ Custom app log file not yet created (will be created when signals fire)"
    fi
else
    echo "✗ Logs directory does not exist"
fi

echo ""
echo "=========================================="
echo "Verification Complete!"
echo "=========================================="
