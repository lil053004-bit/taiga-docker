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

# Check events RabbitMQ vhosts
echo "2. Events RabbitMQ vhosts:"
echo "-------------------------"
docker exec project-taiga-events-rabbitmq-1 rabbitmqctl list_vhosts 2>/dev/null || echo "Error: Cannot access events RabbitMQ"
echo ""

# Check async RabbitMQ vhosts
echo "3. Async RabbitMQ vhosts:"
echo "------------------------"
docker exec project-taiga-async-rabbitmq-1 rabbitmqctl list_vhosts 2>/dev/null || echo "Error: Cannot access async RabbitMQ"
echo ""

# Check recent backend logs for errors
echo "4. Recent Backend Logs (checking for errors):"
echo "---------------------------------------------"
docker logs project-taiga-back-1 --tail 20 2>/dev/null | grep -i "error\|exception" | tail -5 || echo "No recent errors found"
echo ""

# Check events service logs
echo "5. Events Service Status:"
echo "------------------------"
docker logs project-taiga-events-1 --tail 10 2>/dev/null || echo "Error: Cannot access events logs"
echo ""

# Summary
echo "=========================================="
echo "Verification Summary:"
echo "=========================================="
echo ""
echo "✓ If you see 'taiga' in both RabbitMQ vhost lists above, the fix is successful!"
echo "✓ If containers show 'Up' status, services are running"
echo "✓ If no 'vhost taiga not found' errors appear, RabbitMQ is configured correctly"
echo ""
echo "Next step: Try creating a project in the Taiga web interface"
echo "=========================================="
