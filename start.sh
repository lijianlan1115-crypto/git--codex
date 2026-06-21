#!/bin/bash
# ============================================
# V27 AI 分析服务一键启动脚本
# ============================================

echo "🚀 启动 V27 AI 分析服务..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建：python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 启动 FastAPI 服务器（后台运行）
echo "🔧 启动 FastAPI 服务器..."
uvicorn server:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &
SERVER_PID=$!

# 等待服务器启动
sleep 3

# 检查服务器是否启动成功
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ FastAPI 服务器启动成功"
else
    echo "❌ FastAPI 服务器启动失败，请检查 server.log"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# 启动 Cloudflare 隧道
echo "🌐 启动 Cloudflare 隧道..."
cloudflared tunnel --url http://localhost:8080