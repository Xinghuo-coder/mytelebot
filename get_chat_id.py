#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取群组 CHAT_ID
"""

import asyncio
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters
import config

print("=" * 60)
print("🔍 获取群组 CHAT_ID")
print("=" * 60)
print("\n📝 步骤：")
print("1. 确保机器人已添加到目标群组")
print("2. 在群组中发送任意消息（@机器人或直接发消息）")
print("3. 等待显示群组信息...\n")
print("⏳ 监听中，请在群组发送消息...")
print("-" * 60)

async def message_handler(update: Update, context):
    """处理消息并显示群组信息"""
    chat = update.effective_chat
    user = update.effective_user
    
    print(f"\n✅ 收到消息！")
    print(f"📍 来源: {chat.type}")
    
    if chat.type in ['group', 'supergroup']:
        print(f"🏷️ 群组名称: {chat.title}")
        print(f"🆔 群组 ID: {chat.id}")
        print(f"\n" + "=" * 60)
        print(f"✨ 请将以下 CHAT_ID 复制到 config.py：")
        print(f"\nCHAT_ID = \"{chat.id}\"")
        print("=" * 60)
    elif chat.type == 'private':
        print(f"👤 私聊用户: {user.first_name}")
        print(f"🆔 用户 ID: {chat.id}")
        print(f"\n⚠️ 这是私聊，不是群组")
        print(f"请在群组中发送消息来获取群组ID")
    
    # 收到一条消息后就退出
    import sys
    sys.exit(0)

async def main():
    """主函数"""
    application = Application.builder().token(config.BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, message_handler))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 已停止")
