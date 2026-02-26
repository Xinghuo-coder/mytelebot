#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试发送消息 - 验证机器人配置是否正确
"""

import asyncio
import sys
from telegram import Bot
from telegram.error import TelegramError
import config

async def test_send_message():
    """测试发送消息到群组"""
    print("=" * 60)
    print("🧪 测试机器人发送消息功能")
    print("=" * 60)
    
    # 检查配置
    print("\n1️⃣ 检查配置...")
    if config.BOT_TOKEN == "YOUR_BOT_TOKEN" or not config.BOT_TOKEN:
        print("   ❌ BOT_TOKEN 未配置")
        print("\n请先配置 config.py 文件中的 BOT_TOKEN")
        return False
    
    if config.CHAT_ID == "YOUR_CHAT_ID" or not config.CHAT_ID:
        print("   ❌ CHAT_ID 未配置")
        print("\n请先配置 config.py 文件中的 CHAT_ID")
        return False
    
    print(f"   ✅ BOT_TOKEN: {config.BOT_TOKEN[:10]}...{config.BOT_TOKEN[-10:]}")
    print(f"   ✅ CHAT_ID: {config.CHAT_ID}")
    
    # 测试连接
    print("\n2️⃣ 测试机器人连接...")
    try:
        bot = Bot(token=config.BOT_TOKEN)
        me = await bot.get_me()
        print(f"   ✅ 机器人连接成功")
        print(f"   🤖 机器人名称: {me.first_name}")
        print(f"   🆔 机器人用户名: @{me.username}")
    except TelegramError as e:
        print(f"   ❌ 连接失败: {e}")
        print("\n可能原因：")
        print("   - BOT_TOKEN 不正确")
        print("   - 网络连接问题")
        return False
    
    # 测试发送消息
    print("\n3️⃣ 测试发送消息到群组...")
    try:
        message = await bot.send_message(
            chat_id=config.CHAT_ID,
            text="🧪 <b>测试消息</b>\n\n这是一条测试消息，用于验证机器人配置是否正确。\n\n✅ 如果你看到这条消息，说明机器人配置成功！",
            parse_mode='HTML'
        )
        print(f"   ✅ 消息发送成功！")
        print(f"   📝 消息ID: {message.message_id}")
        print(f"   💬 发送到: {message.chat.title if message.chat.title else message.chat.type}")
        return True
    except TelegramError as e:
        print(f"   ❌ 发送失败: {e}")
        print("\n可能原因：")
        if "chat not found" in str(e).lower():
            print("   - CHAT_ID 不正确")
            print("   - 机器人未添加到该群组")
        elif "bot was blocked" in str(e).lower():
            print("   - 机器人被群组封禁")
        elif "not enough rights" in str(e).lower():
            print("   - 机器人没有发送消息的权限")
        else:
            print("   - 请检查群组设置")
            print("   - 确保机器人在群组中")
            print("   - 确保机器人有发送消息权限")
        return False

async def main():
    success = await test_send_message()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！机器人配置正确。")
        print("\n🚀 现在可以运行主程序了：")
        print("   python3 bot.py")
    else:
        print("❌ 测试失败，请检查配置。")
        print("\n💡 解决方案：")
        print("   1. 检查 config.py 中的 BOT_TOKEN 和 CHAT_ID")
        print("   2. 确保机器人已添加到群组")
        print("   3. 确保机器人有管理员权限或发送消息权限")
        print("   4. 运行诊断: python3 check_config.py")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
