#!/bin/bash

set -e

echo "=========================================="
echo "Taiga 一键部署脚本"
echo "Taiga One-Command Deployment"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

if [ ! -f .env ]; then
    echo "✗ 错误：找不到 .env 文件！"
    echo "✗ Error: .env file not found!"
    exit 1
fi

echo "✓ Configuration file found"
echo ""

echo "第1步：停止现有服务..."
echo "Step 1: Stopping existing services..."
docker compose down
echo "✓ Services stopped"
echo ""

echo "第2步：启动所有服务..."
echo "Step 2: Starting all services..."
docker compose up -d
echo "✓ Services started"
echo ""

echo "第3步：等待服务就绪（30秒）..."
echo "Step 3: Waiting for services to be ready (30 seconds)..."
sleep 30
echo "✓ Services should be ready"
echo ""

echo "第4步：运行初始化..."
echo "Step 4: Running initialization..."
bash initialize.sh
echo ""

echo "第5步：验证部署..."
echo "Step 5: Verifying deployment..."
if [ -f scripts/verify_installation.sh ]; then
    bash scripts/verify_installation.sh
else
    echo "⚠ Verification script not found (optional)"
fi
echo ""

echo "=========================================="
echo "✓ 部署完成！"
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "访问地址 / Access URLs:"
echo "  主页 / Main: https://kairui.lhwebs.com"
echo "  管理面板 / Admin: https://kairui.lhwebs.com/admin/"
echo ""
echo "登录信息 / Login Credentials:"
echo "  用户名 / Username: adsadmin"
echo "  密码 / Password: A52290120a"
echo ""
echo "常用命令 / Useful Commands:"
echo "  查看状态 / Check status: docker compose ps"
echo "  查看日志 / View logs: docker compose logs -f"
echo "  重启服务 / Restart: docker compose restart"
echo "  停止服务 / Stop: docker compose down"
echo ""
echo "重要提示 / Important Notes:"
echo "  1. 首次访问请清除浏览器缓存"
echo "     Clear browser cache on first access"
echo "  2. 使用无痕模式可避免缓存问题"
echo "     Use incognito mode to avoid cache issues"
echo "  3. 如遇401错误，请确认Nginx配置已加载"
echo "     If you see 401 errors, verify Nginx config is loaded"
echo ""
