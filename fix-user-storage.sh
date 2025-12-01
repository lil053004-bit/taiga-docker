#!/bin/bash

# Fix Taiga user-storage API 404 error
# This script runs database migrations to create missing user-storage tables

set -e

echo "=========================================="
echo "Fixing User-Storage API"
echo "=========================================="
echo ""

echo "Step 1: Checking if backend container is running..."
if docker ps | grep -q "project-taiga-back-1"; then
    echo "✓ Backend container is running"
else
    echo "✗ Backend container is not running"
    echo "Please start Taiga first with: bash launch-taiga.sh"
    exit 1
fi

echo ""
echo "Step 2: Running database migrations..."
bash taiga-manage.sh migrate

echo ""
echo "Step 3: Checking for user-storage related tables..."
docker exec project-taiga-db-1 psql -U taiga -d taiga -c "\dt" | grep -i storage || echo "No storage tables found"

echo ""
echo "Step 4: Checking backend logs for errors..."
docker logs project-taiga-back-1 --tail 30 | grep -i "storage\|migration" | tail -10 || echo "No relevant logs found"

echo ""
echo "=========================================="
echo "✓ Migration complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Refresh your browser (Ctrl+F5 or Cmd+Shift+R)"
echo "  2. Check browser console (F12)"
echo "  3. The 404 error on /api/v1/user-storage should be gone"
echo ""
echo "If the error persists, check the logs:"
echo "  docker logs project-taiga-back-1 --tail 50"
echo ""
