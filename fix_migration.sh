#!/bin/bash

# Taiga Migration Fix Script
# This script fixes the "column already exists" migration error

set -e

echo "=========================================="
echo "Taiga Migration Fix Script"
echo "=========================================="
echo ""

echo "Step 1: Checking Docker containers status..."
docker compose ps

echo ""
echo "Step 2: Faking the problematic migration..."
echo "This tells Django the migration was already applied."
docker compose exec -T taiga-back python manage.py migrate custom_attributes 0013_auto_20181022_1624 --fake

echo ""
echo "Step 3: Running all remaining migrations..."
docker compose exec -T taiga-back python manage.py migrate

echo ""
echo "Step 4: Collecting static files..."
docker compose exec -T taiga-back python manage.py collectstatic --noinput || true

echo ""
echo "=========================================="
echo "Migration Fix Complete!"
echo "=========================================="
echo ""
echo "Now you can run the initialization script:"
echo "  bash initialize.sh"
echo ""
