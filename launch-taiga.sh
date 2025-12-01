#!/usr/bin/env bash

# Taiga Launch Script
# Starts all Taiga services with automatic initialization

set -e

echo "=========================================="
echo "Launching Taiga"
echo "=========================================="
echo ""

if [ ! -f ".env" ]; then
    echo "✗ Error: .env file not found!"
    echo "  Please create .env file with your configuration."
    exit 1
fi

echo "✓ Configuration file found"
echo ""

echo "Starting Docker containers..."
docker compose up -d

echo ""
echo "Waiting for services to initialize (60 seconds)..."
sleep 60

echo ""
echo "=========================================="
echo "✓ Taiga Started Successfully!"
echo "=========================================="
echo ""
echo "Services are now running at:"
echo "  Main URL: https://kairui.lhwebs.com"
echo "  Admin Panel: https://kairui.lhwebs.com/admin/"
echo ""
echo "Default Login Credentials:"
echo "  Username: adsadmin"
echo "  Password: A52290120a"
echo ""
echo "Check status: docker compose ps"
echo "View logs: docker compose logs -f"
echo ""
