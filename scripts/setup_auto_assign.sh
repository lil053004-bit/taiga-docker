#!/bin/bash

set -e

echo "=========================================="
echo "🎯 Taiga Auto-Assign Setup Script"
echo "=========================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "📋 Step 1: Checking configuration..."
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

source .env

if [ -z "$AUTO_ASSIGN_ADMIN_USERNAME" ]; then
    echo "⚠️  Warning: AUTO_ASSIGN_ADMIN_USERNAME not set in .env"
    echo "   Using default: adsadmin"
fi

echo "✅ Configuration found"
echo "   Admin: ${AUTO_ASSIGN_ADMIN_USERNAME:-adsadmin}"
echo "   Email: ${AUTO_ASSIGN_ADMIN_EMAIL:-lhweave@gmail.com}"
echo ""

echo "📋 Step 2: Creating logs directory..."
mkdir -p logs
chmod 777 logs
echo "✅ Logs directory ready"
echo ""

echo "📋 Step 3: Stopping Taiga services..."
docker compose down
echo "✅ Services stopped"
echo ""

echo "📋 Step 4: Starting Taiga services with new configuration..."
docker compose up -d
echo "✅ Services starting..."
echo ""

echo "📋 Step 5: Waiting for services to be ready (30 seconds)..."
sleep 30
echo "✅ Services should be ready"
echo ""

echo "📋 Step 6: Running Django management command to add admin to all projects..."
echo ""
docker compose -f docker-compose.yml -f docker-compose-inits.yml run --rm taiga-manage add_admin_to_all_projects --username=adsadmin

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "   1. Check logs: tail -f logs/auto_assign.log"
echo "   2. Create a new project to test auto-add"
echo "   3. Create a user story to test auto-assign"
echo ""
echo "🔧 Management commands available:"
echo "   - Add admin to all projects:"
echo "     ./taiga-manage.sh add_admin_to_all_projects"
echo ""
echo "   - Fix unassigned items:"
echo "     ./taiga-manage.sh fix_unassigned_items"
echo ""
echo "=========================================="
