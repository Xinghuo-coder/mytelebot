#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置检查脚本 - 诊断机器人配置问题
"""

import sys
import config

def check_config():
    """检查配置是否正确"""
    print("=" * 60)
    print("🔍 机器人配置诊断")
    print("=" * 60)
    
    issues = []
    
    # 检查 BOT_TOKEN
    print("\n1️⃣ 检查 BOT_TOKEN...")
    if config.BOT_TOKEN == "YOUR_BOT_TOKEN" or not config.BOT_TOKEN:
        print("   ❌ BOT_TOKEN 未配置")
        issues.append("BOT_TOKEN 需要从 @BotFather 获取")
    elif ":" not in config.BOT_TOKEN:
        print("   ⚠️ BOT_TOKEN 格式可能不正确")
        issues.append("BOT_TOKEN 格式应为: 123456789:ABCdefGHIjklMNO...")
    else:
        print(f"   ✅ BOT_TOKEN 已配置 (长度: {len(config.BOT_TOKEN)} 字符)")
    
    # 检查 CHAT_ID
    print("\n2️⃣ 检查 CHAT_ID...")
    if config.CHAT_ID == "YOUR_CHAT_ID" or not config.CHAT_ID:
        print("   ❌ CHAT_ID 未配置")
        issues.append("CHAT_ID 需要获取群组ID")
    elif not str(config.CHAT_ID).startswith("-"):
        print(f"   ⚠️ CHAT_ID = {config.CHAT_ID}")
        print("   ⚠️ 群组ID通常以负号开头（如：-1001234567890）")
        issues.append("请确认 CHAT_ID 是否正确（群组ID应以 - 开头）")
    else:
        print(f"   ✅ CHAT_ID 已配置: {config.CHAT_ID}")
    
    # 检查定时配置
    print("\n3️⃣ 检查定时任务配置...")
    print(f"   📅 定时类型: {config.SCHEDULE_TYPE}")
    if config.SCHEDULE_TYPE == "daily":
        print(f"   ⏰ 推送时间: {config.SCHEDULE_HOURS} 点")
    
    # 检查AI配置
    print("\n4️⃣ 检查 AI 配置...")
    if config.AI_ENABLED:
        if config.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
            print("   ⚠️ AI 功能已启用但 GEMINI_API_KEY 未配置")
            issues.append("需要从 https://makersuite.google.com/app/apikey 获取 API Key")
        else:
            print(f"   ✅ AI 功能已启用 (模型: {config.GEMINI_MODEL})")
    else:
        print("   ℹ️ AI 功能未启用")
    
    # 检查推特监控
    print("\n5️⃣ 检查推特监控配置...")
    if config.TRUMP_TWITTER_ENABLED:
        print(f"   ✅ 推特监控已启用 (用户: @{config.TRUMP_TWITTER_USERNAME})")
        print(f"   ⏱️ 检查间隔: {config.TRUMP_CHECK_INTERVAL} 分钟")
    else:
        print("   ℹ️ 推特监控未启用")
    
    # 汇总问题
    print("\n" + "=" * 60)
    if issues:
        print("❌ 发现以下问题：\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        print("\n" + "=" * 60)
        print("\n📝 如何获取配置：")
        print("\n【获取 BOT_TOKEN】")
        print("  1. 在 Telegram 搜索 @BotFather")
        print("  2. 发送 /mybots 查看你的机器人")
        print("  3. 选择机器人 → API Token")
        
        print("\n【获取群组 CHAT_ID】")
        print("  1. 将机器人添加到你的群组")
        print("  2. 在群里发送任意消息")
        print("  3. 访问以下网址（替换你的BOT_TOKEN）：")
        print("     https://api.telegram.org/bot你的BOT_TOKEN/getUpdates")
        print("  4. 找到 \"chat\":{\"id\":-1001234567890}")
        print("  5. 群组ID必须包含负号（如：-1001234567890）")
        
        print("\n【配置步骤】")
        print("  1. 编辑 config.py 文件")
        print("  2. 替换 BOT_TOKEN 和 CHAT_ID")
        print("  3. 保存文件")
        print("  4. 运行: python bot.py")
        print("\n" + "=" * 60)
        return False
    else:
        print("✅ 所有配置检查通过！")
        print("=" * 60)
        print("\n🚀 可以启动机器人了：")
        print("   python bot.py")
        print("=" * 60)
        return True

if __name__ == "__main__":
    success = check_config()
    sys.exit(0 if success else 1)
