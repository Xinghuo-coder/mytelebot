#!/bin/bash
# 重启 bot.py

echo "🔄 准备重启 bot.py..."

# 查找bot.py进程
PID=$(ps aux | grep -v grep | grep "bot.py" | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "❌ 未找到正在运行的 bot.py 进程"
    echo "💡 启动新进程..."
else
    echo "📋 找到进程 PID: $PID"
    echo "🛑 停止旧进程..."
    kill $PID
    sleep 2
    
    # 确认进程已停止
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  进程未停止，强制终止..."
        kill -9 $PID
        sleep 1
    fi
    echo "✅ 旧进程已停止"
fi

# 启动新进程
echo "🚀 启动新进程..."
cd /Users/macbookpro/telebot

# 激活虚拟环境并在后台运行bot
nohup /Users/macbookpro/telebot/.venv/bin/python /Users/macbookpro/telebot/bot.py > bot.log 2> bot_error.log &

NEW_PID=$!
sleep 2

# 检查新进程是否启动成功
if ps -p $NEW_PID > /dev/null 2>&1; then
    echo "✅ bot.py 已启动，PID: $NEW_PID"
    echo "📋 查看日志: tail -f /Users/macbookpro/telebot/bot_error.log"
else
    echo "❌ bot.py 启动失败，请检查日志"
    tail -20 /Users/macbookpro/telebot/bot_error.log
fi
