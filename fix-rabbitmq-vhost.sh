#!/bin/bash

# Fix RabbitMQ vhost issue for Taiga
# This script creates the missing 'taiga' vhost in both RabbitMQ containers

set -e

echo "=========================================="
echo "Fixing RabbitMQ vhost configuration"
echo "=========================================="

# Check if containers are running
echo ""
echo "Step 1: Checking container status..."
docker compose ps | grep rabbitmq || true

# Function to setup vhost in a container
setup_vhost() {
    local container=$1
    echo ""
    echo "Setting up vhost in $container..."

    # Wait for RabbitMQ to be ready
    echo "Waiting for RabbitMQ to be ready..."
    sleep 5

    # Check if vhost already exists
    if docker exec $container rabbitmqctl list_vhosts | grep -q "^taiga$"; then
        echo "✓ vhost 'taiga' already exists in $container"
    else
        echo "Creating vhost 'taiga' in $container..."
        docker exec $container rabbitmqctl add_vhost taiga
        echo "✓ vhost 'taiga' created"
    fi

    # Set permissions
    echo "Setting permissions for user 'taiga' on vhost 'taiga'..."
    docker exec $container rabbitmqctl set_permissions -p taiga taiga ".*" ".*" ".*"
    echo "✓ Permissions set"

    # List vhosts to verify
    echo "Current vhosts in $container:"
    docker exec $container rabbitmqctl list_vhosts
}

# Setup vhost in events RabbitMQ
echo ""
echo "Step 2: Configuring taiga-events-rabbitmq..."
setup_vhost "project-taiga-events-rabbitmq-1"

# Setup vhost in async RabbitMQ
echo ""
echo "Step 3: Configuring taiga-async-rabbitmq..."
setup_vhost "project-taiga-async-rabbitmq-1"

# Restart related services
echo ""
echo "Step 4: Restarting Taiga services..."
docker compose restart taiga-back taiga-events taiga-async

echo ""
echo "=========================================="
echo "✓ RabbitMQ vhost configuration complete!"
echo "=========================================="
echo ""
echo "Please wait 10-20 seconds for services to fully restart,"
echo "then try creating a project again."
echo ""
