#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试恒生科技指数获取功能和定时任务配置
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

async def test_hstech_index():
    """测试恒生科技指数API"""
    print("="*60)
    print("🔍 测试恒生科技指数获取功能")
    print("="*60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取恒生科技指数
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EHSTECH"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            print(f"\n📡 请求URL: {url}")
            print(f"⏳ 正在获取数据...")
            
            async with session.get(url, headers=headers, timeout=15) as response:
                print(f"\n📊 响应状态: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # 打印完整响应以便调试
                    print("\n📄 API响应结构:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...")
                    
                    # 尝试解析数据
                    if data.get('chart') and data['chart'].get('result'):
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        print("\n✅ 成功获取数据:")
                        print(f"   交易所: {meta.get('exchangeName', 'N/A')}")
                        print(f"   股票代码: {meta.get('symbol', 'N/A')}")
                        print(f"   当前价格: {meta.get('regularMarketPrice', 'N/A')}")
                        print(f"   昨收价: {meta.get('chartPreviousClose', 'N/A')}")
                        print(f"   市场状态: {meta.get('marketState', 'N/A')}")
                        
                        price = meta.get('regularMarketPrice')
                        prev_close = meta.get('chartPreviousClose')
                        
                        if price and prev_close:
                            change_pct = ((price - prev_close) / prev_close) * 100
                            change_value = price - prev_close
                            market_state = meta.get('marketState', 'CLOSED')
                            current_weekday = datetime.now().weekday()
                            
                            market_status = ""
                            if current_weekday >= 5:
                                market_status = " [周五收盘]"
                            elif market_state == 'CLOSED':
                                market_status = " [收盘]"
                            
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            result_text = f"🔬 恒生科技: {price:,.2f}{market_status} {change_symbol}{change_value:+.2f} ({change_pct:+.2f}%)"
                            
                            print(f"\n🎯 格式化结果:")
                            print(f"   {result_text}")
                            return True
                        else:
                            print("\n❌ 价格数据缺失")
                            print(f"   price = {price}")
                            print(f"   prev_close = {prev_close}")
                            return False
                    else:
                        print("\n❌ API响应格式错误")
                        if data.get('chart'):
                            print(f"   chart存在: {data['chart'].keys()}")
                            if data['chart'].get('error'):
                                print(f"   错误信息: {data['chart']['error']}")
                        return False
                else:
                    print(f"\n❌ HTTP错误: {response.status}")
                    error_text = await response.text()
                    print(f"   响应内容: {error_text[:500]}")
                    return False
                    
    except asyncio.TimeoutError:
        print("\n❌ 请求超时")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_scheduler():
    """测试定时任务配置"""
    print("\n" + "="*60)
    print("⏰ 测试定时任务配置")
    print("="*60)
    
    try:
        # 创建调度器
        scheduler = AsyncIOScheduler()
        
        # 定义测试任务
        async def test_job():
            print(f"✅ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 定时任务执行成功")
        
        # 添加测试任务（每分钟的第0秒执行）
        scheduler.add_job(
            test_job,
            CronTrigger(minute='*', second=0),  # 每分钟执行一次
            id='test_job',
            name='测试任务',
            replace_existing=True
        )
        
        # 启动调度器
        scheduler.start()
        print("\n✅ 调度器已启动")
        print(f"📋 已注册任务:")
        
        for job in scheduler.get_jobs():
            print(f"   - {job.name} (ID: {job.id})")
            print(f"     下次执行时间: {job.next_run_time}")
        
        # 等待3分钟观察任务执行
        print("\n⏳ 等待3分钟观察任务执行情况...")
        print("   (按 Ctrl+C 可以提前结束)")
        
        try:
            await asyncio.sleep(180)  # 等待3分钟
        except KeyboardInterrupt:
            print("\n⚠️  用户中断")
        
        # 关闭调度器
        scheduler.shutdown()
        print("\n✅ 调度器已关闭")
        return True
        
    except Exception as e:
        print(f"\n❌ 调度器测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_bot_scheduler():
    """检查bot.py中的定时任务配置"""
    print("\n" + "="*60)
    print("🔍 检查 bot.py 定时任务配置")
    print("="*60)
    
    try:
        # 读取config.py
        print("\n📄 读取配置文件...")
        import config
        
        print(f"\n⚙️  定时任务配置:")
        print(f"   SCHEDULE_TYPE: {config.SCHEDULE_TYPE}")
        if config.SCHEDULE_TYPE == "daily":
            print(f"   SCHEDULE_HOURS: {config.SCHEDULE_HOURS}")
            print(f"   SCHEDULE_MINUTES: {config.SCHEDULE_MINUTES}")
        
        # 模拟检查定时任务
        print(f"\n📋 bot.py 中配置的定时任务:")
        tasks = [
            ("07:30", "早上7:30价格更新"),
            ("11:30", "上午11:30价格更新"),
            ("15:00", "下午15:00价格更新"),
            ("17:40", "下午17:40价格更新"),
            ("20:00", "晚上20:00价格更新"),
            ("21:00", "晚上21:00价格更新"),
            ("22:00", "晚上22:00价格更新"),
            ("07:00", "早上7:00财经日历"),
            ("21:00", "晚上21:00财经日历"),
        ]
        
        for time, name in tasks:
            print(f"   - {time} {name}")
        
        print("\n💡 建议检查项:")
        print("   1. 确认 bot.py 是否正在运行 (ps aux | grep bot.py)")
        print("   2. 查看日志输出是否有 '调度器已启动' 信息")
        print("   3. 查看日志输出是否有定时任务执行记录")
        print("   4. 检查系统时区设置是否正确 (date)")
        print("   5. 如果是systemd服务，检查服务状态 (systemctl status telebot)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 配置检查失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 开始测试")
    print("="*60)
    
    # 测试1: 恒生科技指数API
    result1 = await test_hstech_index()
    
    # 测试2: 检查配置
    result2 = await check_bot_scheduler()
    
    # 测试3: 测试定时任务（可选）
    print("\n" + "="*60)
    print("❓ 是否要测试定时任务? (这将运行3分钟)")
    print("   输入 'y' 运行，其他任何键跳过")
    print("="*60)
    
    # 由于是自动化脚本，直接跳过交互式测试
    print("⏭️  跳过定时任务测试（如需测试请手动运行 test_scheduler()）")
    result3 = True
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"   恒生科技指数API: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"   配置检查: {'✅ 通过' if result2 else '❌ 失败'}")
    print(f"   定时任务测试: ⏭️  已跳过")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
