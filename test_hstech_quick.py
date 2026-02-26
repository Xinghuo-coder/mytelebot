#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试恒生科技指数
"""

import asyncio
import aiohttp
from datetime import datetime

async def test_hstech():
    """测试恒生科技指数"""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/HSTECH.HK"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('chart') and data['chart'].get('result'):
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
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
                            
                            print("✅ 恒生科技指数获取成功!")
                            print(f"   {result_text}")
                            return result_text
                        
                print("❌ 获取失败")
                return "🔬 恒生科技: --"
    except Exception as e:
        print(f"❌ 错误: {e}")
        return "🔬 恒生科技: --"

if __name__ == '__main__':
    asyncio.run(test_hstech())
