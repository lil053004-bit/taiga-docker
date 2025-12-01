#!/bin/bash

# Taiga Migration Fix Script
# This script fixes the "column already exists" migration error
# and ensures smooth redeployment

set -e

echo "=========================================="
echo "Taiga Migration Fix Script"
echo "=========================================="
echo ""

echo "Step 1: Checking Docker containers status..."
if ! docker compose ps; then
    echo "✗ Docker containers are not running!"
    echo "Please start them first: docker compose up -d"
    exit 1
fi

echo ""
echo "Step 2: Checking if fix is needed..."
if docker compose exec -T taiga-back python manage.py migrate --plan 2>&1 | grep -q "custom_attributes"; then
    echo "  - Migration issues detected, applying fix..."

    echo ""
    echo "Step 3: Faking problematic custom_attributes migrations..."
    echo "  This tells Django the migrations were already applied."
    docker compose exec -T taiga-back python manage.py migrate custom_attributes --fake

    echo ""
    echo "Step 4: Running all remaining migrations..."
    docker compose exec -T taiga-back python manage.py migrate

    echo "  ✓ Migrations fixed successfully"
else
    echo "  ✓ No migration issues detected"
    echo ""
    echo "Step 3: Running migrations normally..."
    docker compose exec -T taiga-back python manage.py migrate
fi

echo ""
echo "Step 5: Collecting static files..."
docker compose exec -T taiga-back python manage.py collectstatic --noinput || true

echo ""
echo "=========================================="
echo "Migration Fix Complete!"
echo "=========================================="
echo ""
echo "The system is now ready. You can:"
echo "  1. Run initialization: bash initialize.sh"
echo "  2. Or access directly: https://${TAIGA_DOMAIN:-kairui.lhwebs.com}"
echo ""
echo "This fix will prevent the error on future redeployments."
echo ""
