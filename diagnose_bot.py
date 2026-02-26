#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的机器人诊断工具 - 检测所有问题
"""

import asyncio
import sys
import json
import aiohttp
import config

class BotDiagnostics:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.bot_info = None
        
    def add_issue(self, msg):
        self.issues.append(msg)
        
    def add_warning(self, msg):
        self.warnings.append(msg)
    
    async def check_bot_token(self):
        """检查 BOT_TOKEN 有效性"""
        print("\n" + "="*60)
        print("1️⃣ 检查 BOT_TOKEN")
        print("="*60)
        
        if config.BOT_TOKEN == "YOUR_BOT_TOKEN" or not config.BOT_TOKEN:
            print("❌ BOT_TOKEN 未配置")
            self.add_issue("BOT_TOKEN 未配置")
            return False
        
        try:
            # 使用 HTTP API 而不是 python-telegram-bot 来避免冲突
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getMe"
                async with session.get(url) as response:
                    data = await response.json()
                    
                    if data.get('ok'):
                        self.bot_info = data['result']
                        print(f"✅ BOT_TOKEN 有效")
                        print(f"   🤖 机器人名称: {self.bot_info['first_name']}")
                        print(f"   🆔 用户名: @{self.bot_info['username']}")
                        return True
                    else:
                        print(f"❌ BOT_TOKEN 无效: {data.get('description')}")
                        self.add_issue("BOT_TOKEN 无效或已过期")
                        return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            self.add_issue(f"无法连接到 Telegram API: {e}")
            return False
    
    async def check_chat_id(self):
        """检查 CHAT_ID 配置"""
        print("\n" + "="*60)
        print("2️⃣ 检查 CHAT_ID 配置")
        print("="*60)
        
        if config.CHAT_ID == "YOUR_CHAT_ID" or not config.CHAT_ID:
            print("❌ CHAT_ID 未配置")
            self.add_issue("CHAT_ID 未配置")
            return False
        
        print(f"ℹ️  当前配置: CHAT_ID = {config.CHAT_ID}")
        
        # 检查格式
        chat_id_str = str(config.CHAT_ID)
        if not chat_id_str.startswith("-"):
            print("⚠️  群组ID通常以负号开头")
            self.add_warning("CHAT_ID 不是负数，可能不是群组")
        
        return True
    
    async def test_chat_access(self):
        """测试对群组的访问权限"""
        print("\n" + "="*60)
        print("3️⃣ 测试群组访问权限")
        print("="*60)
        
        try:
            async with aiohttp.ClientSession() as session:
                # 尝试获取群组信息
                url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getChat"
                params = {'chat_id': config.CHAT_ID}
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data.get('ok'):
                        chat_info = data['result']
                        print(f"✅ 可以访问群组")
                        print(f"   📝 群组名称: {chat_info.get('title', 'N/A')}")
                        print(f"   🆔 群组ID: {chat_info['id']}")
                        print(f"   📊 类型: {chat_info['type']}")
                        
                        if chat_info['type'] == 'private':
                            print("⚠️  这是私聊，不是群组！")
                            self.add_warning("CHAT_ID 指向的是私聊而不是群组")
                        
                        return True
                    else:
                        error_desc = data.get('description', '未知错误')
                        print(f"❌ 无法访问群组: {error_desc}")
                        
                        if 'chat not found' in error_desc.lower():
                            print("\n   可能原因：")
                            print("   • CHAT_ID 不正确")
                            print("   • 机器人未添加到该群组")
                            print("   • 机器人已被移除")
                            self.add_issue("群组不存在或机器人不在群组中")
                        elif 'bot was blocked' in error_desc.lower():
                            print("\n   可能原因：")
                            print("   • 机器人被群组封禁")
                            self.add_issue("机器人被封禁")
                        else:
                            self.add_issue(f"无法访问群组: {error_desc}")
                        
                        return False
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            self.add_issue(f"检查群组访问时出错: {e}")
            return False
    
    async def check_send_permission(self):
        """检查发送消息权限"""
        print("\n" + "="*60)
        print("4️⃣ 测试发送消息")
        print("="*60)
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': config.CHAT_ID,
                    'text': '🧪 诊断测试消息\n\n这是一条自动测试消息，用于验证机器人配置。',
                    'parse_mode': 'HTML'
                }
                
                async with session.post(url, json=data) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        print(f"✅ 成功发送测试消息！")
                        print(f"   📝 消息ID: {result['result']['message_id']}")
                        return True
                    else:
                        error_desc = result.get('description', '未知错误')
                        print(f"❌ 发送失败: {error_desc}")
                        
                        if 'not enough rights' in error_desc.lower():
                            print("\n   原因：机器人没有发送消息的权限")
                            print("   解决：在群组设置中给予机器人发送消息权限")
                            self.add_issue("机器人没有发送消息权限")
                        elif 'chat not found' in error_desc.lower():
                            self.add_issue("群组不存在或机器人不在群组中")
                        else:
                            self.add_issue(f"发送消息失败: {error_desc}")
                        
                        return False
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            self.add_issue(f"测试发送消息时出错: {e}")
            return False
    
    async def get_available_chats(self):
        """获取机器人可访问的所有群组"""
        print("\n" + "="*60)
        print("5️⃣ 查找可用的群组")
        print("="*60)
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates"
                params = {'limit': 100, 'timeout': 0}
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if not data.get('ok'):
                        print(f"⚠️  无法获取更新: {data.get('description')}")
                        return
                    
                    updates = data.get('result', [])
                    
                    if not updates:
                        print("⚠️  没有找到任何消息记录")
                        print("\n   💡 建议：")
                        print("   1. 将机器人添加到目标群组")
                        print("   2. 在群组中发送任意消息")
                        print("   3. 重新运行此诊断")
                        return
                    
                    # 收集所有群组
                    chats = {}
                    for update in updates:
                        msg = update.get('message') or update.get('my_chat_member')
                        if msg and msg.get('chat'):
                            chat = msg['chat']
                            chat_id = chat['id']
                            chat_type = chat['type']
                            
                            if chat_type in ['group', 'supergroup']:
                                if chat_id not in chats:
                                    chats[chat_id] = {
                                        'id': chat_id,
                                        'title': chat.get('title', 'Unknown'),
                                        'type': chat_type
                                    }
                    
                    if chats:
                        print(f"✅ 找到 {len(chats)} 个群组：\n")
                        for i, (chat_id, info) in enumerate(chats.items(), 1):
                            is_current = (str(chat_id) == str(config.CHAT_ID))
                            marker = " 👈 当前配置" if is_current else ""
                            print(f"   {i}. {info['title']}{marker}")
                            print(f"      ID: {chat_id}")
                            print(f"      类型: {info['type']}")
                            print()
                        
                        # 如果当前CHAT_ID不在列表中
                        if str(config.CHAT_ID) not in [str(cid) for cid in chats.keys()]:
                            print("⚠️  当前配置的 CHAT_ID 不在可用群组列表中！")
                            print(f"\n   💡 建议更新 config.py：")
                            recommended = list(chats.values())[0]
                            print(f'\n   CHAT_ID = "{recommended["id"]}"  # {recommended["title"]}')
                            self.add_issue("配置的 CHAT_ID 不在机器人可访问的群组中")
                    else:
                        print("ℹ️  没有找到群组消息")
                        print("   机器人可能：")
                        print("   • 未添加到任何群组")
                        print("   • 添加后还没有人发言")
                        
        except Exception as e:
            print(f"⚠️  查找群组失败: {e}")
    
    async def check_other_instances(self):
        """检查是否有其他实例在运行"""
        print("\n" + "="*60)
        print("6️⃣ 检查冲突的机器人实例")
        print("="*60)
        
        try:
            # 尝试使用长轮询获取更新
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates"
                params = {'timeout': 1, 'limit': 1}
                
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    data = await response.json()
                    
                    if data.get('ok'):
                        print("✅ 没有检测到冲突的实例")
                        return True
                    else:
                        error = data.get('description', '')
                        if 'conflict' in error.lower():
                            print("❌ 检测到冲突！")
                            print("   有另一个机器人实例正在运行")
                            print("\n   可能位置：")
                            print("   • 同一台电脑的其他终端")
                            print("   • 云服务器（如 AWS、阿里云等）")
                            print("   • 其他电脑或设备")
                            self.add_issue("有其他机器人实例正在运行，造成冲突")
                            return False
                        return True
        except asyncio.TimeoutError:
            print("✅ 没有检测到冲突的实例")
            return True
        except Exception as e:
            print(f"⚠️  检查失败: {e}")
            return True
    
    def print_summary(self):
        """打印诊断总结"""
        print("\n" + "="*60)
        print("📊 诊断总结")
        print("="*60)
        
        if not self.issues and not self.warnings:
            print("\n🎉 恭喜！所有检查都通过了！")
            print("\n✅ 机器人配置正确，可以正常运行")
            print("\n🚀 启动机器人：")
            print("   python3 bot.py")
        else:
            if self.issues:
                print(f"\n❌ 发现 {len(self.issues)} 个问题：")
                for i, issue in enumerate(self.issues, 1):
                    print(f"   {i}. {issue}")
            
            if self.warnings:
                print(f"\n⚠️  {len(self.warnings)} 个警告：")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"   {i}. {warning}")
            
            print("\n" + "="*60)
            print("💡 解决建议")
            print("="*60)
            
            if any('CHAT_ID' in issue for issue in self.issues):
                print("\n【群组ID问题】")
                print("1. 确保机器人已添加到目标群组")
                print("2. 在群组中发送任意消息")
                print("3. 重新运行诊断，查看可用群组列表")
                print("4. 更新 config.py 中的 CHAT_ID")
            
            if any('冲突' in issue or 'conflict' in issue.lower() for issue in self.issues):
                print("\n【实例冲突】")
                print("1. 停止所有运行中的机器人实例")
                print("   killall -9 python3")
                print("2. 检查云服务器是否有实例在运行")
                print("3. 等待1-2分钟后再启动")
        
        print("\n" + "="*60)

async def main():
    """主诊断流程"""
    print("="*60)
    print("🔍 机器人完整诊断工具")
    print("="*60)
    print("正在检查所有配置和权限...\n")
    
    diag = BotDiagnostics()
    
    # 执行所有检查
    token_ok = await diag.check_bot_token()
    if not token_ok:
        diag.print_summary()
        return 1
    
    await diag.check_chat_id()
    await diag.test_chat_access()
    await diag.check_send_permission()
    await diag.get_available_chats()
    await diag.check_other_instances()
    
    # 打印总结
    diag.print_summary()
    
    return 0 if not diag.issues else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
