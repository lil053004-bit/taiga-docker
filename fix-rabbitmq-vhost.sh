#!/bin/bash

# Fix RabbitMQ vhost and user configuration for Taiga
# This script creates the missing 'taiga' user and vhost in both RabbitMQ containers

set -e

# Load environment variables
source .env

echo "=========================================="
echo "Fixing RabbitMQ configuration"
echo "=========================================="

# Check if containers are running
echo ""
echo "Step 1: Checking container status..."
docker compose ps | grep rabbitmq || true

# Function to setup RabbitMQ in a container
setup_rabbitmq() {
    local container=$1
    echo ""
    echo "Setting up RabbitMQ in $container..."

    # Wait for RabbitMQ to be ready
    echo "Waiting for RabbitMQ to be ready..."
    sleep 5

    # Check if user exists
    if docker exec $container rabbitmqctl list_users | grep -q "^taiga"; then
        echo "✓ User 'taiga' already exists in $container"
    else
        echo "Creating user 'taiga' in $container..."
        docker exec $container rabbitmqctl add_user taiga "${RABBITMQ_PASS}"
        docker exec $container rabbitmqctl set_user_tags taiga administrator
        echo "✓ User 'taiga' created"
    fi

    # Check if vhost exists
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

    # List users and vhosts to verify
    echo "Current users in $container:"
    docker exec $container rabbitmqctl list_users
    echo "Current vhosts in $container:"
    docker exec $container rabbitmqctl list_vhosts
}

# Setup RabbitMQ in events container
echo ""
echo "Step 2: Configuring taiga-events-rabbitmq..."
setup_rabbitmq "project-taiga-events-rabbitmq-1"

# Setup RabbitMQ in async container
echo ""
echo "Step 3: Configuring taiga-async-rabbitmq..."
setup_rabbitmq "project-taiga-async-rabbitmq-1"

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
