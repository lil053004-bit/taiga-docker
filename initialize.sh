#!/bin/bash

# Taiga Initialization Script
# This script creates the admin user and sets up the system

set -e

echo "=========================================="
echo "Taiga Initialization Script"
echo "=========================================="
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
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
