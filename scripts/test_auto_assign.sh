#!/bin/bash

set -e

echo "=========================================="
echo "🧪 Taiga Auto-Assign Test Script"
echo "=========================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "📋 Test 1: Check if services are running..."
if docker compose ps | grep -q "Up"; then
    echo "✅ Services are running"
else
    echo "❌ Services are not running. Start with: docker compose up -d"
    exit 1
fi
echo ""

echo "📋 Test 2: Check if custom module is mounted..."
if docker compose exec -T taiga-back test -d /taiga-back/custom; then
    echo "✅ Custom module is mounted"
else
    echo "❌ Custom module not found in container"
    exit 1
fi
echo ""

echo "📋 Test 3: Check if config.py is loaded..."
if docker compose exec -T taiga-back test -f /taiga-back/settings/config.py; then
    echo "✅ Config file is mounted"
else
    echo "❌ Config file not found"
    exit 1
fi
echo ""

echo "📋 Test 4: Check if admin user exists..."
ADMIN_EXISTS=$(docker exec -i taiga-db psql -U taiga -d taiga -t -c \
    "SELECT COUNT(*) FROM users_user WHERE username = 'adsadmin';" | tr -d ' ')

if [ "$ADMIN_EXISTS" -gt 0 ]; then
    echo "✅ Admin user 'adsadmin' exists"
else
    echo "⚠️  Admin user 'adsadmin' not found"
    echo "   Create the admin user first via Django admin or manage.py"
fi
echo ""

echo "📋 Test 5: Check environment variables..."
AUTO_ENABLED=$(docker compose exec -T taiga-back env | grep AUTO_ASSIGN_ENABLED || echo "NOT_SET")
if echo "$AUTO_ENABLED" | grep -q "True"; then
    echo "✅ AUTO_ASSIGN_ENABLED is True"
else
    echo "⚠️  AUTO_ASSIGN_ENABLED is not set to True"
    echo "   Current value: $AUTO_ENABLED"
fi
echo ""

echo "📋 Test 6: Check project count and admin membership..."
docker exec -i taiga-db psql -U taiga -d taiga << EOF
SELECT
    COUNT(DISTINCT p.id) as total_projects,
    COUNT(DISTINCT CASE WHEN m.user_id = u.id THEN m.project_id END) as projects_with_admin,
    COUNT(DISTINCT CASE WHEN m.user_id = u.id THEN m.project_id END)::float /
        NULLIF(COUNT(DISTINCT p.id), 0) * 100 as coverage_percentage
FROM projects_project p
CROSS JOIN users_user u
LEFT JOIN projects_membership m ON p.id = m.project_id AND m.user_id = u.id
WHERE u.username = 'adsadmin';
EOF
echo ""

echo "📋 Test 7: Check unassigned items..."
docker exec -i taiga-db psql -U taiga -d taiga << EOF
SELECT
    'User Stories' as type,
    COUNT(*) as unassigned_count
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
echo ""

echo "📋 Test 8: Check recent log entries..."
if [ -f logs/auto_assign.log ]; then
    echo "Last 5 log entries:"
    tail -5 logs/auto_assign.log || echo "No recent logs"
else
    echo "⚠️  Log file not found at logs/auto_assign.log"
    echo "   Create with: mkdir -p logs && touch logs/auto_assign.log && chmod 666 logs/auto_assign.log"
fi
echo ""

echo "=========================================="
echo "🧪 Test Summary"
echo "=========================================="
echo ""
echo "✅ Tests completed. Check results above."
echo ""
echo "📝 Next steps:"
echo "   1. If admin user doesn't exist, create it in Django admin"
echo "   2. Run: ./taiga-manage.sh add_admin_to_all_projects"
echo "   3. Create a test project and verify admin is added"
echo "   4. Create a test user story and verify it's assigned"
echo ""
echo "=========================================="
