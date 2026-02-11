#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试财经日历功能
"""

import asyncio
import aiohttp
from datetime import datetime


async def get_financial_calendar():
    """获取今日财经日历"""
    # 定义每周重要财经事件时间表（作为后备）
    weekday_events = {
        0: [  # 周一
            "无固定重要事件"
        ],
        1: [  # 周二
            "⭐⭐ 09:30 🇨🇳 中国CPI数据（每月）",
            "⭐⭐⭐ 20:30 🇺🇸 美国CPI数据（每月）",
        ],
        2: [  # 周三
            "⭐⭐ 09:30 🇨🇳 中国PPI数据（每月）",
            "⭐⭐⭐ 02:00 🇺🇸 美联储会议纪要（不定期）",
        ],
        3: [  # 周四
            "⭐⭐⭐ 20:30 🇺🇸 美国初请失业金人数（每周）",
            "⭐⭐ 22:00 🇺🇸 美国新屋销售（每月）",
        ],
        4: [  # 周五
            "⭐⭐⭐ 20:30 🇺🇸 美国非农就业数据（每月首个周五）",
            "⭐⭐ 09:30 🇨🇳 中国制造业PMI（每月）",
        ],
        5: [  # 周六
            "休市日"
        ],
        6: [  # 周日
            "休市日"
        ],
    }
    
    try:
        # 获取今天是星期几
        today_weekday = datetime.now().weekday()
        print(f"今天是星期{['一', '二', '三', '四', '五', '六', '日'][today_weekday]}")
        
        # 生成今日财经日历
        events = []
        
        # 添加今日固定事件
        fixed_events = weekday_events.get(today_weekday, [])
        print(f"\n今日固定事件: {len(fixed_events)} 条")
        
        for event in fixed_events:
            if event not in ["无固定重要事件", "休市日"]:
                events.append({
                    'time': event.split()[1] if len(event.split()) > 1 else '待定',
                    'info': event,
                    'importance': 3 if '⭐⭐⭐' in event else 2
                })
        
        # 添加常规性重要事件提醒
        current_day = datetime.now().day
        print(f"当前日期: {current_day}号")
        
        # 每月初（1-5号）提醒重要数据发布日
        if 1 <= current_day <= 5:
            events.append({
                'time': '本周',
                'info': '⭐⭐⭐ 本周关注：美国非农就业、中国CPI/PPI数据发布',
                'importance': 3
            })
            print("✓ 添加月初重要数据提醒")
        
        # 美联储决议周（通常每月中下旬）
        if 15 <= current_day <= 20:
            events.append({
                'time': '本月',
                'info': '⭐⭐⭐ 本月关注：美联储利率决议（FOMC会议）',
                'importance': 3
            })
            print("✓ 添加美联储决议提醒")
        
        # 如果是周五，特别提醒非农
        if today_weekday == 4 and 1 <= current_day <= 7:
            events.append({
                'time': '20:30',
                'info': '⭐⭐⭐ 20:30 🇺🇸 美国非农就业数据 (本月首个周五)',
                'importance': 3
            })
            print("✓ 添加非农数据特别提醒")
        
        if events:
            print(f"\n✅ 生成财经日历 {len(events)} 条")
            return events
        
        # 如果是周末，返回休市提示
        if today_weekday >= 5:
            print("✓ 今日为周末")
            return [{
                'time': '全天',
                'info': '📅 今日市场休市',
                'importance': 1
            }]
        
        # 默认返回一些通用提醒
        print("✓ 使用默认通用提醒")
        return [{
            'time': '全天',
            'info': '📊 今日关注：主要货币汇率、贵金属价格、原油价格波动',
            'importance': 2
        }]
        
    except Exception as e:
        print(f"\n❌ 获取财经日历失败: {e}")
        import traceback
        traceback.print_exc()
        return []
    """获取今日财经日历"""
    try:
        async with aiohttp.ClientSession() as session:
            # 方案1：使用金十数据网页版财经日历
            url = "https://flash.jin10.com/get_calendar?day=0"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://rili.jin10.com/',
                'Accept': 'application/json',
            }
            
            print(f"方案1: 金十数据")
            print(f"请求: {url}")
            try:
                async with session.get(url, headers=headers, timeout=15) as response:
                    print(f"状态码: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"响应类型: {type(result)}")
                        
                        # 解析数据结构
                        events = []
                        if isinstance(result, dict) and 'data' in result:
                            data = result['data']
                            print(f"数据段数: {len(data) if isinstance(data, list) else 'N/A'}")
                            
                            # 遍历时间段
                            for time_slot in data:
                                if isinstance(time_slot, dict) and 'events' in time_slot:
                                    for event in time_slot['events']:
                                        importance = event.get('star', 0)
                                        if importance >= 2:  # 只获取重要事件
                                            time = event.get('time', '')
                                            country = event.get('country', '')
                                            event_name = event.get('event', '')
                                            unit = event.get('unit', '')
                                            previous = event.get('previous', '')
                                            forecast = event.get('forecast', '')
                                            
                                            # 格式化事件信息
                                            event_info = f"{time} {country} {event_name}"
                                            if forecast:
                                                event_info += f" (预期: {forecast}{unit})"
                                            if previous:
                                                event_info += f" (前值: {previous}{unit})"
                                            
                                            events.append({
                                                'time': time,
                                                'info': event_info,
                                                'importance': importance
                                            })
                        
                        if events:
                            # 按时间排序
                            events.sort(key=lambda x: x['time'])
                            print(f"✅ 金十数据: 获取到 {len(events)} 条事件")
                            return events
                        else:
                            print("⚠️ 金十数据: 无重要事件")
            except Exception as e:
                print(f"❌ 金十数据失败: {e}")
            
            # 方案2：使用财联社API
            print(f"\n方案2: 财联社")
            url2 = "https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=7.7.5&way=calendar"
            headers2 = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://www.cls.cn/',
            }
            
            print(f"请求: {url2}")
            try:
                async with session.get(url2, headers=headers2, timeout=15) as response:
                    print(f"状态码: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        events = []
                        
                        if isinstance(result, dict) and 'data' in result:
                            data = result['data']
                            print(f"数据条数: {len(data) if isinstance(data, list) else 'N/A'}")
                            
                            if isinstance(data, list):
                                for item in data:
                                    # 提取重要信息
                                    time = item.get('time', '')
                                    title = item.get('title', '')
                                    importance_level = item.get('importance', 0)
                                    
                                    if importance_level >= 2 and title:
                                        events.append({
                                            'time': time,
                                            'info': f"{time} {title}",
                                            'importance': importance_level
                                        })
                        
                        if events:
                            print(f"✅ 财联社: 获取到 {len(events)} 条事件")
                            return events
                        else:
                            print("⚠️ 财联社: 无重要事件")
            except Exception as e:
                print(f"❌ 财联社失败: {e}")
            
            # 方案3：使用东方财富网财经日历
            print(f"\n方案3: 东方财富")
            today = datetime.now().strftime('%Y-%m-%d')
            url3 = f"https://datacenter-web.eastmoney.com/api/data/get?type=RPT_ECONOMICDATA_CALENDAR&sty=ALL&filter=(REPORTDATE='{today}')"
            headers3 = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://data.eastmoney.com/',
            }
            
            print(f"请求: {url3[:100]}...")
            try:
                async with session.get(url3, headers=headers3, timeout=15) as response:
                    print(f"状态码: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        events = []
                        
                        if isinstance(result, dict) and 'result' in result:
                            data_list = result['result'].get('data', [])
                            print(f"数据条数: {len(data_list)}")
                            
                            for item in data_list:
                                time = item.get('PUBLISH_TIME', '')
                                country = item.get('COUNTRY', '')
                                indicator = item.get('INDICATOR_NAME', '')
                                importance = item.get('IMPORTANCE', 0)
                                
                                if importance >= 2 and indicator:
                                    event_info = f"{time} {country} {indicator}"
                                    
                                    forecast = item.get('PREDICTED_VALUE', '')
                                    previous = item.get('PREVIOUS_VALUE', '')
                                    
                                    if forecast:
                                        event_info += f" (预期: {forecast})"
                                    if previous:
                                        event_info += f" (前值: {previous})"
                                    
                                    events.append({
                                        'time': time,
                                        'info': event_info,
                                        'importance': importance
                                    })
                        
                        if events:
                            events.sort(key=lambda x: x['time'])
                            print(f"✅ 东方财富: 获取到 {len(events)} 条事件")
                            return events
                        else:
                            print("⚠️ 东方财富: 无重要事件")
            except Exception as e:
                print(f"❌ 东方财富失败: {e}")
            
            print("\n❌ 所有数据源均无法获取财经日历")
            return []
            
    except Exception as e:
        print(f"\n❌ 获取财经日历失败: {e}")
        import traceback
        traceback.print_exc()
        return []


async def test_calendar():
    """测试财经日历"""
    print("=" * 60)
    print("财经日历获取测试")
    print("=" * 60)
    
    events = await get_financial_calendar()
    
    if events:
        print("\n" + "=" * 60)
        print("今日财经日历预览")
        print("=" * 60)
        
        current_date = datetime.now().strftime('%Y年%m月%d日')
        print(f"\n📅 {current_date} 财经日历\n")
        
        for event in events[:15]:
            importance = event['importance']
            stars = '⭐' * importance
            print(f"{stars} {event['info']}")
        
        if len(events) > 15:
            print(f"\n... 还有 {len(events) - 15} 个其他事件")
    else:
        print("\n⚠️ 没有获取到财经日历数据")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_calendar())
