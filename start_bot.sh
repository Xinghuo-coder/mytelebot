#!/bin/bash
cd /Users/macbookpro/telebot

# 停止所有bot进程
echo "停止旧进程..."
pkill -9 -f "bot.py"
sleep 3

# 启动新进程
echo "启动新进程..."
/Users/macbookpro/telebot/.venv/bin/python /Users/macbookpro/telebot/bot.py > bot.log 2> bot_error.log &

sleep 2
echo "Done! 进程PID: $!"
ps aux | grep -v grep | grep "bot.py"
