#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试上证指数获取功能
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_sse_index():
    """测试上证指数API"""
    print("="*60)
    print("🔍 测试上证指数获取功能")
    print("="*60)
    
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取上证指数
            url = "https://query1.finance.yahoo.com/v8/finance/chart/000001.SS"
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
                        print(f"   交易日: {meta.get('tradingPeriods', 'N/A')}")
                        
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
                            result_text = f"📊 上证指数: {price:.2f}{market_status} {change_symbol}{change_value:+.2f} ({change_pct:+.2f}%)"
                            
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

async def test_alternative_sources():
    """测试其他数据源"""
    print("\n" + "="*60)
    print("🔄 测试替代数据源")
    print("="*60)
    
    # 测试东方财富网API
    print("\n1️⃣ 测试东方财富网API...")
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'secid': '1.000001',  # 上证指数
                'fields': 'f43,f44,f45,f46,f57,f58,f59,f60,f170',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://quote.eastmoney.com/'
            }
            
            async with session.get(url, params=params, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ 响应成功")
                    print(f"   数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                    
                    if data.get('data'):
                        quote = data['data']
                        price = quote.get('f43')  # 最新价
                        prev_close = quote.get('f60')  # 昨收
                        
                        if price and prev_close:
                            # 价格单位是分，需要除以100
                            price = price / 100
                            prev_close = prev_close / 100
                            change_pct = ((price - prev_close) / prev_close) * 100
                            
                            print(f"\n   📊 上证指数: {price:.2f} ({change_pct:+.2f}%)")
                            return True
                else:
                    print(f"   ❌ HTTP错误: {response.status}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试新浪财经API
    print("\n2️⃣ 测试新浪财经API...")
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://hq.sinajs.cn/list=s_sh000001"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    print(f"   ✅ 响应成功")
                    print(f"   数据: {text[:200]}...")
                    
                    # 解析数据: var hq_str_s_sh000001="上证指数,3000.00,10.00,0.33%,...";
                    if '"' in text:
                        data_str = text.split('"')[1]
                        parts = data_str.split(',')
                        if len(parts) >= 4:
                            name = parts[0]
                            price = float(parts[1])
                            change = float(parts[2])
                            change_pct = parts[3]
                            
                            print(f"\n   📊 {name}: {price:.2f} ({change_pct})")
                            return True
                else:
                    print(f"   ❌ HTTP错误: {response.status}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    return False

async def main():
    print("\n开始测试...\n")
    
    # 测试Yahoo Finance
    success = await test_sse_index()
    
    # 如果失败，测试其他数据源
    if not success:
        print("\n⚠️  Yahoo Finance API失败，尝试其他数据源...")
        await test_alternative_sources()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
