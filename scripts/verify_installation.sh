#!/bin/bash

echo "================================================================"
echo "Taiga Enhanced Features - Installation Verification"
echo "================================================================"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

ERRORS=0
WARNINGS=0

echo "Checking backend files..."
echo ""

check_file() {
    if [ -f "$1" ]; then
        echo "✓ $1"
        return 0
    else
        echo "✗ $1 - MISSING!"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

check_file "taiga-custom/admin.py"
check_file "taiga-custom/views.py"
check_file "taiga-custom/urls.py"
check_file "taiga-custom/importers.py"
check_file "taiga-custom/serializers.py"
check_file "taiga-custom/management/commands/set_users_chinese.py"

echo ""
echo "Checking frontend files..."
echo ""

check_file "taiga-front/conf.json"
check_file "taiga-front/custom-fields.js"
check_file "taiga-front/custom-fields.css"

echo ""
echo "Checking docker-compose.yml configuration..."
echo ""

if grep -q "DEFAULT_USER_LANGUAGE" docker-compose.yml; then
    echo "✓ Language environment variable configured"
else
    echo "⚠ DEFAULT_USER_LANGUAGE not found in docker-compose.yml"
    WARNINGS=$((WARNINGS + 1))
fi

if grep -q "taiga-front/conf.json" docker-compose.yml; then
    echo "✓ Frontend volumes configured"
else
    echo "✗ Frontend volumes not configured in docker-compose.yml"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "Checking signals.py for language setting..."
echo ""

if grep -q "set_default_language_chinese" taiga-custom/signals.py; then
    echo "✓ Language signal implemented"
else
    echo "✗ Language signal not found"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "Checking config.py..."
echo ""

if grep -q "DEFAULT_USER_LANGUAGE" taiga-custom/config.py; then
    echo "✓ DEFAULT_USER_LANGUAGE configured"
else
    echo "⚠ DEFAULT_USER_LANGUAGE not in config.py"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "================================================================"
echo "Verification Summary"
echo "================================================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✓✓✓ ALL CHECKS PASSED! ✓✓✓"
    echo ""
    echo "Your installation is complete and ready to use!"
    echo ""
    echo "Next steps:"
    echo "1. docker compose exec taiga-back python manage.py set_users_chinese"
    echo "2. docker compose restart taiga-front taiga-back"
    echo "3. Visit https://yourdomain.com/admin/"
    echo ""
elif [ $ERRORS -eq 0 ]; then
    echo "✓ Installation complete with $WARNINGS warning(s)"
    echo ""
    echo "Warnings are non-critical but should be reviewed."
    echo ""
else
    echo "✗ Installation incomplete!"
    echo ""
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "Please fix the errors above before proceeding."
    echo ""
fi

echo "================================================================"

exit $ERRORS
