#!/bin/bash

echo "================================================================"
echo "Taiga Custom Fields Display - Setup Script"
echo "================================================================"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "✓ Project root: $PROJECT_ROOT"
echo ""

echo "Checking prerequisites..."
echo ""

if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found!"
    echo "   Please run this script from the Taiga project root directory."
    exit 1
fi

echo "✓ docker-compose.yml found"

if [ ! -d "taiga-front" ]; then
    echo "⚠ taiga-front directory not found. Creating..."
    mkdir -p taiga-front
    echo "✓ Created taiga-front directory"
fi

echo "✓ taiga-front directory exists"
echo ""

echo "Checking configuration files..."
echo ""

if [ -f "taiga-front/conf.json" ]; then
    echo "✓ conf.json exists"
else
    echo "⚠ conf.json not found (should have been created during implementation)"
fi

if [ -f "taiga-front/custom-fields.js" ]; then
    echo "✓ custom-fields.js exists"
else
    echo "⚠ custom-fields.js not found (should have been created during implementation)"
fi

if [ -f "taiga-front/custom-fields.css" ]; then
    echo "✓ custom-fields.css exists"
else
    echo "⚠ custom-fields.css not found (should have been created during implementation)"
fi

echo ""
echo "Checking Docker Compose configuration..."
echo ""

if grep -q "taiga-front/conf.json" docker-compose.yml; then
    echo "✓ Frontend volumes are configured in docker-compose.yml"
else
    echo "⚠ Frontend volumes not found in docker-compose.yml"
    echo "  Please ensure the following volumes are mounted in taiga-front service:"
    echo "    - ./taiga-front/conf.json:/usr/share/nginx/html/conf.json:ro"
    echo "    - ./taiga-front/custom-fields.js:/usr/share/nginx/html/custom-fields.js:ro"
    echo "    - ./taiga-front/custom-fields.css:/usr/share/nginx/html/custom-fields.css:ro"
fi

echo ""
echo "================================================================"
echo "Setup Complete!"
echo "================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Set all users to Chinese language:"
echo "   docker compose exec taiga-back python manage.py set_users_chinese"
echo ""
echo "2. Restart services to apply changes:"
echo "   docker compose restart taiga-front taiga-back"
echo ""
echo "3. Access Django Admin for export/import:"
echo "   https://yourdomain.com/admin/"
echo "   Login with your superuser account"
echo ""
echo "4. Verify custom fields display:"
echo "   - Open any project in Taiga"
echo "   - Go to Kanban or Backlog view"
echo "   - Custom fields should appear on cards"
echo ""
echo "================================================================"
