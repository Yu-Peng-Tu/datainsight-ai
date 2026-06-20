#!/bin/bash
# DataInsight AI 一键部署脚本
# 使用方式：先配置好 Vercel 和 Render 账号，然后运行此脚本

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo "  DataInsight AI 部署脚本"
echo "========================================"
echo ""
echo "⚠️  部署前请确认："
echo "   1. 已注册 Vercel 账号 (vercel.com)"
echo "   2. 已注册 Render 账号 (render.com)"
echo "   3. 已安装 Vercel CLI: npm install -g vercel"
echo ""
read -p "确认以上已完成，按 Enter 继续..."

echo ""
echo "========================================"
echo "  步骤 1: Vercel CLI 登录"
echo "========================================"
echo "即将打开浏览器进行 Vercel 授权..."
vercel login

echo ""
echo "========================================"
echo "  步骤 2: 部署前端到 Vercel"
echo "========================================"
cd "$PROJECT_ROOT/frontend"

# 检查是否已构建
if [ ! -d "dist" ]; then
    echo "正在构建前端..."
    npm run build
fi

echo "正在部署到 Vercel..."
vercel deploy --prod --yes

echo ""
echo "✅ 前端部署完成！"
echo ""

echo "========================================"
echo "  步骤 3: Render 后端部署说明"
echo "========================================"
echo ""
echo "由于 Render 需要浏览器授权，请手动完成："
echo ""
echo "1. 打开 https://dashboard.render.com"
echo "2. 点击 New → Web Service"
echo "3. 连接 GitHub 仓库: Yu-Peng-Tu/datainsight-ai"
echo "4. 配置如下："
echo "   - Name: datainsight-ai-backend"
echo "   - Runtime: Python 3"
echo "   - Build Command: cd backend && pip install -r requirements.txt"
echo "   - Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo "5. 在 Environment 中添加:"
echo "   MOONSHOT_API_KEY=你的APIKey"
echo "6. 点击 Create Web Service"
echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "前端地址: https://datainsight-ai-frontend.vercel.app (部署后可见)"
echo "后端地址: https://datainsight-ai-backend.onrender.com (部署后可见)"
echo ""
echo "⚠️  重要: 前端代码中的 API 地址需要修改为你实际的 Render 地址："
echo "   修改 frontend/src/api/client.ts 中的 baseURL"
echo "   然后重新运行: vercel deploy --prod"
