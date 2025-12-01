#!/bin/bash

# Verification script to check if RabbitMQ fix was successful

echo "=========================================="
echo "Taiga RabbitMQ Verification"
echo "=========================================="
echo ""

# Check container status
echo "1. Container Status:"
echo "-------------------"
docker compose ps | grep -E "(NAME|taiga-events-rabbitmq|taiga-async-rabbitmq|taiga-back|taiga-events|taiga-async)" || echo "Error: Cannot check containers"
echo ""

# Check events RabbitMQ users
echo "2. Events RabbitMQ Users:"
echo "------------------------"
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_users 2>/dev/null || echo "Error: Cannot access events RabbitMQ"
echo ""

# Check events RabbitMQ vhosts
echo "3. Events RabbitMQ vhosts:"
echo "-------------------------"
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_vhosts 2>/dev/null || echo "Error: Cannot access events RabbitMQ"
echo ""

# Check async RabbitMQ users
echo "4. Async RabbitMQ Users:"
echo "-----------------------"
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_users 2>/dev/null || echo "Error: Cannot access async RabbitMQ"
echo ""

# Check async RabbitMQ vhosts
echo "5. Async RabbitMQ vhosts:"
echo "------------------------"
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_vhosts 2>/dev/null || echo "Error: Cannot access async RabbitMQ"
echo ""

# Check RabbitMQ permissions
echo "6. Events RabbitMQ Permissions on 'taiga' vhost:"
echo "------------------------------------------------"
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_permissions -p taiga 2>/dev/null || echo "Error: Cannot check permissions"
echo ""

echo "7. Async RabbitMQ Permissions on 'taiga' vhost:"
echo "-----------------------------------------------"
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_permissions -p taiga 2>/dev/null || echo "Error: Cannot check permissions"
echo ""

# Check recent backend logs for errors
echo "8. Recent Backend Logs (checking for errors):"
echo "---------------------------------------------"
docker logs project-taiga-back-1 --tail 20 2>/dev/null | grep -i "error\|exception\|rabbitmq" | tail -5 || echo "No recent errors found"
echo ""

# Check events service logs
echo "9. Events Service Status:"
echo "------------------------"
docker logs project-taiga-events-1 --tail 10 2>/dev/null || echo "Error: Cannot access events logs"
echo ""

# Summary
echo "=========================================="
echo "Verification Summary:"
echo "=========================================="
echo ""
echo "Expected Results:"
echo "  ✓ User 'taiga' should exist in both RabbitMQ containers"
echo "  ✓ Vhost 'taiga' should exist in both RabbitMQ containers"
echo "  ✓ User 'taiga' should have full permissions on vhost 'taiga'"
echo "  ✓ All containers should show 'Up' status"
echo "  ✓ No 'vhost taiga not found' or 'User taiga does not exist' errors"
echo ""
echo "If all checks pass, try creating a project at:"
echo "  https://kairui.lhwebs.com"
echo ""
echo "If issues persist:"
echo "  - Try: bash reset-rabbitmq.sh (clean reset)"
echo "  - Or: bash fix-rabbitmq-vhost.sh (manual fix)"
echo "=========================================="
