#!/bin/bash

# Complete RabbitMQ reset for Taiga
# This script removes RabbitMQ data volumes and reinitializes with correct credentials
# WARNING: This will clear RabbitMQ message queues (but preserves database and media)

set -e

echo "=========================================="
echo "Complete RabbitMQ Reset"
echo "=========================================="
echo ""
echo "This script will:"
echo "  1. Stop all Taiga services"
echo "  2. Remove RabbitMQ data volumes"
echo "  3. Restart services with fresh RabbitMQ"
echo ""
echo "⚠️  WARNING: RabbitMQ message queues will be cleared"
echo "✓  Database and media files will be preserved"
echo ""
read -p "Do you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Reset cancelled."
    exit 0
fi

echo ""
echo "Step 1: Stopping all services..."
docker compose down

echo ""
echo "Step 2: Removing RabbitMQ data volumes..."
docker volume rm project_taiga-events-rabbitmq-data || echo "Volume already removed or doesn't exist"
docker volume rm project_taiga-async-rabbitmq-data || echo "Volume already removed or doesn't exist"

echo ""
echo "Step 3: Starting services (this will take 20-30 seconds)..."
bash launch-taiga.sh

echo ""
echo "Step 4: Waiting for services to initialize..."
sleep 30

echo ""
echo "Step 5: Verifying RabbitMQ configuration..."
echo ""
echo "Events RabbitMQ users:"
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_users 2>/dev/null || echo "Container not ready yet"
echo ""
echo "Events RabbitMQ vhosts:"
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_vhosts 2>/dev/null || echo "Container not ready yet"
echo ""
echo "Async RabbitMQ users:"
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_users 2>/dev/null || echo "Container not ready yet"
echo ""
echo "Async RabbitMQ vhosts:"
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_vhosts 2>/dev/null || echo "Container not ready yet"

echo ""
echo "Step 6: Checking backend logs..."
docker logs project-taiga-back-1 --tail 20 2>/dev/null | grep -i "error\|ready" || echo "No errors found"

echo ""
echo "=========================================="
echo "✓ RabbitMQ reset complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Wait another 10 seconds for full initialization"
echo "  2. Go to https://kairui.lhwebs.com"
echo "  3. Try creating a project"
echo ""
echo "If you still have issues, run: bash verify-fix.sh"
echo ""
