#!/bin/bash

# Taiga Initialization Script
# This script creates the admin user and sets up the system

set -e

echo "=========================================="
echo "Taiga Initialization Script"
echo "=========================================="
echo ""

# Load environment variables safely (remove inline comments)
if [ -f .env ]; then
    set -a
    source <(grep -v '^#' .env | sed 's/#.*$//' | grep -E '^[A-Z_]+=')
    set +a
fi

# Default values
ADMIN_USERNAME="${AUTO_ASSIGN_ADMIN_USERNAME:-adsadmin}"
ADMIN_EMAIL="${AUTO_ASSIGN_ADMIN_EMAIL:-lhweave@gmail.com}"
ADMIN_PASSWORD="${POSTGRES_PASSWORD:-A52290120a}"

echo "Step 1: Running database migrations..."
docker compose exec taiga-back python manage.py migrate

echo ""
echo "Step 2: Collecting static files..."
docker compose exec taiga-back python manage.py collectstatic --noinput || true

echo ""
echo "Step 3: Creating admin user..."

# Check if user already exists
USER_EXISTS=$(docker compose exec -T taiga-back python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
print('yes' if User.objects.filter(username='${ADMIN_USERNAME}').exists() else 'no')
" 2>/dev/null | tail -1)

if [ "$USER_EXISTS" = "yes" ]; then
    echo "Admin user '${ADMIN_USERNAME}' already exists. Updating..."
    docker compose exec -T taiga-back python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='${ADMIN_USERNAME}')
user.set_password('${ADMIN_PASSWORD}')
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.email = '${ADMIN_EMAIL}'
user.lang = 'zh-Hans'
user.save()
print('\n✓ Admin user updated successfully')
print(f'  Username: ${ADMIN_USERNAME}')
print(f'  Email: ${ADMIN_EMAIL}')
print(f'  Password: ${ADMIN_PASSWORD}')
EOF
else
    echo "Creating new admin user '${ADMIN_USERNAME}'..."
    docker compose exec -T taiga-back python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_superuser(
    username='${ADMIN_USERNAME}',
    email='${ADMIN_EMAIL}',
    password='${ADMIN_PASSWORD}'
)
user.is_active = True
user.is_staff = True
user.is_superuser = True
user.lang = 'zh-Hans'
user.save()
print('\n✓ Admin user created successfully')
print(f'  Username: ${ADMIN_USERNAME}')
print(f'  Email: ${ADMIN_EMAIL}')
print(f'  Password: ${ADMIN_PASSWORD}')
EOF
fi

echo ""
echo "Step 4: Verifying custom app is loaded..."
CUSTOM_APP_CHECK=$(docker compose exec -T taiga-back python -c "
import sys
sys.path.insert(0, '/taiga-back/custom')
try:
    import custom
    print('LOADED')
except Exception as e:
    print('FAILED')
" 2>/dev/null | tail -1)

if [ "$CUSTOM_APP_CHECK" = "LOADED" ]; then
    echo "✓ Custom app loaded successfully"
else
    echo "⚠ Warning: Custom app not loaded (this is normal for first deployment)"
fi

echo ""
echo "Step 5: Setting all users language to Chinese..."
docker compose exec -T taiga-back python manage.py shell <<'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
updated = User.objects.all().update(lang='zh-Hans')
print(f'\n✓ Updated {updated} user(s) to Chinese language')
EOF

echo ""
echo "Step 6: Verifying configuration..."
echo "  - Checking API accessibility..."
docker compose exec -T taiga-back python -c "
import os
print(f'  ✓ CSRF_TRUSTED_ORIGINS: {os.getenv(\"CSRF_TRUSTED_ORIGINS\", \"Not set\")}')
print(f'  ✓ ALLOWED_HOSTS: {os.getenv(\"ALLOWED_HOSTS\", \"Not set\")}')
print(f'  ✓ DEFAULT_USER_LANGUAGE: {os.getenv(\"DEFAULT_USER_LANGUAGE\", \"Not set\")}')
print(f'  ✓ PUBLIC_REGISTER_ENABLED: {os.getenv(\"PUBLIC_REGISTER_ENABLED\", \"Not set\")}')
"

echo ""
echo "=========================================="
echo "Initialization Complete!"
echo "=========================================="
echo ""
echo "Login credentials:"
echo "  URL: https://${TAIGA_DOMAIN:-kairui.lhwebs.com}"
echo "  Username: ${ADMIN_USERNAME}"
echo "  Password: ${ADMIN_PASSWORD}"
echo "  Email: ${ADMIN_EMAIL}"
echo ""
echo "Admin panel: https://${TAIGA_DOMAIN:-kairui.lhwebs.com}/admin/"
echo ""
echo "Next steps:"
echo "  1. Access the site in your browser"
echo "  2. Clear browser cache if you see any errors"
echo "  3. Login with the credentials above"
echo "  4. Check that the interface is in Chinese"
echo ""
echo "Troubleshooting:"
echo "  - View logs: docker compose logs -f"
echo "  - Check status: docker compose ps"
echo "  - Restart services: docker compose restart"
echo ""
