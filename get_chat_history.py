#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过API获取最新消息和群组ID（无需轮询）
"""

import asyncio
import config
from telegram import Bot

async def get_recent_chats():
    """获取最近的聊天记录"""
    print("=" * 60)
    print("🔍 获取机器人最近的聊天记录")
    print("=" * 60)
    
    try:
        bot = Bot(token=config.BOT_TOKEN)
        
        # 获取机器人信息
        me = await bot.get_me()
        print(f"\n✅ 机器人: @{me.username} ({me.first_name})")
        
        # 获取最新的updates
        print("\n📥 获取最近的消息...")
        updates = await bot.get_updates(limit=100, timeout=5)
        
        if not updates:
            print("\n⚠️ 没有找到任何消息记录")
            print("\n💡 请执行以下步骤：")
            print("1. 将机器人 @skySourcePicBot 添加到目标群组")
            print("2. 在群组中发送任意消息（或使用 /start 命令）")
            print("3. 重新运行此脚本")
            return
        
        # 收集所有群组
        chats = {}
        for update in updates:
            if update.message and update.message.chat:
                chat = update.message.chat
                chat_id = chat.id
                
                if chat.type in ['group', 'supergroup']:
                    if chat_id not in chats:
                        chats[chat_id] = {
                            'id': chat_id,
                            'title': chat.title,
                            'type': chat.type,
                            'message_count': 0
                        }
                    chats[chat_id]['message_count'] += 1
        
        if chats:
            print(f"\n✅ 找到 {len(chats)} 个群组：\n")
            print("-" * 60)
            for i, (chat_id, info) in enumerate(chats.items(), 1):
                print(f"{i}. 群组名称: {info['title']}")
                print(f"   群组ID: {chat_id}")
                print(f"   类型: {info['type']}")
                print(f"   消息数: {info['message_count']}")
                print("-" * 60)
            
            # 推荐配置
            if len(chats) == 1:
                recommended_id = list(chats.keys())[0]
                recommended_title = list(chats.values())[0]['title']
                print(f"\n💡 推荐配置：")
                print(f"\nCHAT_ID = \"{recommended_id}\"  # {recommended_title}")
            else:
                print(f"\n💡 请选择正确的群组ID并更新 config.py")
        else:
            print("\n⚠️ 没有找到群组消息")
            print("\n可能原因：")
            print("- 机器人未添加到任何群组")
            print("- 机器人添加后没有人发送过消息")
            
            # 显示所有消息类型
            print("\n📋 找到的其他聊天：")
            for update in updates[:5]:  # 只显示前5条
                if update.message:
                    chat = update.message.chat
                    if chat.type == 'private':
                        print(f"  私聊: {chat.first_name} (ID: {chat.id})")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")

if __name__ == "__main__":
    asyncio.run(get_recent_chats())
