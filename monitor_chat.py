#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监听群组消息并获取CHAT_ID
使用HTTP方式避免冲突
"""

import asyncio
import aiohttp
import config
from datetime import datetime

async def monitor_messages():
    """实时监听新消息"""
    print("="*60)
    print("🎯 实时监听群组消息")
    print("="*60)
    print(f"\n🤖 机器人: @skySourcePicBot")
    print("\n📝 操作步骤：")
    print("1. 打开 Telegram，进入目标群组")
    print("2. 添加机器人 @skySourcePicBot 到群组")
    print("3. 在群组中发送任意消息（如：测试）")
    print("\n⏳ 正在监听... (按 Ctrl+C 停止)")
    print("-"*60)
    
    last_update_id = 0
    found_chats = {}
    
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    # 使用长轮询获取更新
                    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates"
                    params = {
                        'offset': last_update_id + 1,
                        'timeout': 30,
                        'limit': 10
                    }
                    
                    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=35)) as response:
                        data = await response.json()
                        
                        if not data.get('ok'):
                            error = data.get('description', '未知错误')
                            if 'conflict' in error.lower():
                                print("\n❌ 检测到冲突！")
                                print("   有其他机器人实例正在运行")
                                print("   请先停止其他实例：killall -9 python3")
                                return
                            else:
                                print(f"\n⚠️  API错误: {error}")
                                await asyncio.sleep(5)
                                continue
                        
                        updates = data.get('result', [])
                        
                        for update in updates:
                            update_id = update['update_id']
                            last_update_id = max(last_update_id, update_id)
                            
                            # 处理消息
                            msg = update.get('message')
                            member_update = update.get('my_chat_member')
                            
                            if msg and msg.get('chat'):
                                chat = msg['chat']
                                user = msg.get('from', {})
                                text = msg.get('text', '[媒体消息]')
                                
                                chat_id = chat['id']
                                chat_type = chat['type']
                                
                                # 只关注群组消息
                                if chat_type in ['group', 'supergroup']:
                                    time_str = datetime.now().strftime("%H:%M:%S")
                                    
                                    # 记录群组
                                    if chat_id not in found_chats:
                                        found_chats[chat_id] = {
                                            'title': chat.get('title', 'Unknown'),
                                            'type': chat_type
                                        }
                                        
                                        print(f"\n✨ 发现新群组！")
                                        print(f"   ⏰ {time_str}")
                                        print(f"   📝 群组名称: {chat.get('title')}")
                                        print(f"   🆔 群组ID: {chat_id}")
                                        print(f"   👤 发送者: {user.get('first_name', 'Unknown')}")
                                        print(f"   💬 消息: {text[:50]}...")
                                        print("\n" + "="*60)
                                        print("💡 复制以下配置到 config.py：")
                                        print(f'\nCHAT_ID = "{chat_id}"  # {chat.get("title")}')
                                        print("="*60)
                                    else:
                                        # 已知群组的新消息
                                        print(f"📨 [{time_str}] {chat.get('title')}: {text[:30]}...")
                            
                            # 处理机器人加入/离开群组事件
                            elif member_update and member_update.get('chat'):
                                chat = member_update['chat']
                                new_status = member_update.get('new_chat_member', {}).get('status')
                                
                                if chat['type'] in ['group', 'supergroup']:
                                    time_str = datetime.now().strftime("%H:%M:%S")
                                    
                                    if new_status in ['member', 'administrator']:
                                        print(f"\n🎉 机器人被添加到群组！")
                                        print(f"   ⏰ {time_str}")
                                        print(f"   📝 群组名称: {chat.get('title')}")
                                        print(f"   🆔 群组ID: {chat['id']}")
                                        print(f"   ⚡ 状态: {new_status}")
                                        print("\n" + "="*60)
                                        print("💡 复制以下配置到 config.py：")
                                        print(f'\nCHAT_ID = "{chat["id"]}"  # {chat.get("title")}')
                                        print("="*60)
                                        
                                        found_chats[chat['id']] = {
                                            'title': chat.get('title', 'Unknown'),
                                            'type': chat['type']
                                        }
                                    elif new_status in ['left', 'kicked']:
                                        print(f"\n⚠️  机器人被移除: {chat.get('title')}")
                
                except asyncio.TimeoutError:
                    # 超时是正常的，继续下一轮
                    print(".", end="", flush=True)
                    continue
                except Exception as e:
                    print(f"\n⚠️  错误: {e}")
                    await asyncio.sleep(5)
                    
    except KeyboardInterrupt:
        print("\n\n⏹️  已停止监听")
        
        if found_chats:
            print("\n" + "="*60)
            print("📋 发现的群组列表：")
            print("="*60)
            for chat_id, info in found_chats.items():
                print(f"\n群组名称: {info['title']}")
                print(f"群组ID: {chat_id}")
                print(f"类型: {info['type']}")
            
            print("\n" + "="*60)
            print("💡 下一步：")
            print("="*60)
            print("1. 复制上面的群组ID")
            print("2. 更新 config.py 中的 CHAT_ID")
            print("3. 运行测试: python3 test_send_message.py")
        else:
            print("\n⚠️  没有发现任何群组")
            print("\n💡 请确保：")
            print("1. 机器人 @skySourcePicBot 已添加到群组")
            print("2. 在群组中发送了消息")

if __name__ == "__main__":
    asyncio.run(monitor_messages())
