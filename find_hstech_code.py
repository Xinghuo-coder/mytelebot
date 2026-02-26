#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找恒生科技指数的正确代码
"""

import asyncio
import aiohttp

async def test_hstech_variants():
    """测试不同的恒生科技指数代码"""
    
    variants = [
        ("^HSTECH", "Yahoo恒生科技指数"),
        ("HSTECH.HK", "香港恒生科技指数"),
        ("^HSTI", "恒生科技指数备选1"),
        ("HST.HK", "恒生科技指数备选2"),
        ("3067.HK", "恒生科技ETF"),
        ("03067.HK", "恒生科技ETF备选"),
    ]
    
    print("="*60)
    print("🔍 测试不同的恒生科技指数代码")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        for code, name in variants:
            print(f"\n测试: {name} ({code})")
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{code}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            try:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('chart') and data['chart'].get('result'):
                            result = data['chart']['result'][0]
                            meta = result.get('meta', {})
                            price = meta.get('regularMarketPrice')
                            symbol = meta.get('symbol')
                            exchange = meta.get('exchangeName', 'N/A')
                            
                            if price:
                                print(f"   ✅ 成功! 价格: {price}")
                                print(f"      代码: {symbol}")
                                print(f"      交易所: {exchange}")
                            else:
                                print(f"   ⚠️  响应成功但无价格数据")
                        else:
                            error = data.get('chart', {}).get('error', {})
                            print(f"   ❌ 错误: {error.get('description', '未知错误')}")
                    else:
                        print(f"   ❌ HTTP {response.status}")
            except Exception as e:
                print(f"   ❌ 异常: {e}")
            
            await asyncio.sleep(0.5)  # 避免请求过快

if __name__ == '__main__':
    asyncio.run(test_hstech_variants())
