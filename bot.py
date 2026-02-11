#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电报机器人 - 定时发送金融价格信息 + AI问答功能
"""

import asyncio
import logging
from datetime import datetime
import aiohttp
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from telegram.error import TelegramError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import google.generativeai as genai
import config

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 配置信息
BOT_TOKEN = config.BOT_TOKEN
CHAT_ID = config.CHAT_ID

# 初始化机器人
bot = Bot(token=BOT_TOKEN)

# 初始化 Google Gemini
if config.AI_ENABLED:
    genai.configure(api_key=config.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(config.GEMINI_MODEL)


async def get_gold_price():
    """获取伦敦金价格 - 使用fx168news.com"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用fx168news.com作为数据源
            url = "https://www.fx168news.com/quote/XAU"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # 解析JSON数据 (页面包含Next.js数据)
                    import json
                    import re
                    
                    # 提取JSON数据
                    pattern = r'"infoListData":\[({[^}]+})\]'
                    match = re.search(pattern, html)
                    
                    if match:
                        try:
                            info_data = json.loads(match.group(1))
                            
                            price = float(info_data.get('tradePrice', 0))
                            prev_close = float(info_data.get('preClosePrice', 0))
                            range_percent = info_data.get('rangePercent', '')
                            
                            if price > 0 and prev_close > 0:
                                # 解析涨跌幅
                                change_pct = ((price - prev_close) / prev_close) * 100
                                
                                # 检查市场状态
                                current_weekday = datetime.now().weekday()
                                market_status = ""
                                if current_weekday >= 5:  # 周末
                                    market_status = " [周五收盘]"
                                
                                change_symbol = "📈" if change_pct >= 0 else "📉"
                                return f"💰 伦敦金: ${price:.2f}/盎司{market_status} {change_symbol}{change_pct:+.2f}%"
                        except (json.JSONDecodeError, ValueError) as e:
                            logger.error(f"解析fx168数据失败: {e}")
                    
                return "💰 伦敦金: --"
    except Exception as e:
        logger.error(f"获取伦敦金价格失败: {e}")
        return "💰 伦敦金: --"


async def get_dollar_index():
    """获取美元指数"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance API
            url = "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB"
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
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"💵 美元指数: {price:.2f} {change_symbol}{change_pct:+.2f}%"
                logger.warning(f"美元指数API返回数据格式异常")
                return "💵 美元指数: --"
    except asyncio.TimeoutError:
        logger.error("获取美元指数超时")
        return "💵 美元指数: 超时"
    except Exception as e:
        logger.error(f"获取美元指数失败: {e}")
        return "💵 美元指数: --"


async def get_oil_price():
    """获取原油价格（WTI）"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取WTI原油期货价格
            url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F"
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
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"🛢️ WTI原油: ${price:.2f} {change_symbol}{change_pct:+.2f}%"
                logger.warning("原油价格API返回数据格式异常")
                return "🛢️ WTI原油: --"
    except asyncio.TimeoutError:
        logger.error("获取原油价格超时")
        return "🛢️ WTI原油: 超时"
    except Exception as e:
        logger.error(f"获取原油价格失败: {e}")
        return "🛢️ WTI原油: --"


async def get_usdcny_rate():
    """获取美元兑人民币汇率"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取USD/CNY汇率
            url = "https://query1.finance.yahoo.com/v8/finance/chart/CNY=X"
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
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"💴 美元/人民币: ¥{price:.4f} {change_symbol}{change_pct:+.2f}%"
                logger.warning("USD/CNY汇率API返回数据格式异常")
                return "💴 美元/人民币: --"
    except asyncio.TimeoutError:
        logger.error("获取USD/CNY汇率超时")
        return "💴 美元/人民币: 超时"
    except Exception as e:
        logger.error(f"获取USD/CNY汇率失败: {e}")
        return "💴 美元/人民币: --"


async def get_shanghai_gold_price():
    """获取上海金价格 - 从东方财富网API获取"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用东方财富网API获取上海金实时行情
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'secid': '118.SHAU',  # 上海黄金交易所-上海金
                'fields': 'f43,f44,f45,f46,f60,f169,f170',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://quote.eastmoney.com/'
            }
            
            async with session.get(url, params=params, headers=headers, timeout=15) as response:
                if response.status == 200:
                    import json
                    data = await response.json()
                    
                    if data.get('data'):
                        quote = data['data']
                        
                        # 东方财富网价格字段说明:
                        # f43: 最新价 (闭市时为0，单位: 分，需要除以100)
                        # f60: 昨收价 (单位: 分，需要除以100)
                        # f170: 涨跌幅百分比 (单位: 百分点的100倍，需要除以100)
                        price = quote.get('f43', 0)  # 最新价
                        prev_close = quote.get('f60', 0)  # 昨收
                        change_pct = quote.get('f170', 0)  # 涨跌幅
                        
                        # 价格需要除以100转换为元/克
                        if price > 0:
                            price = price / 100
                        if prev_close > 0:
                            prev_close = prev_close / 100
                        # 涨跌幅需要除以100转换为百分比
                        if change_pct != 0:
                            change_pct = change_pct / 100
                        
                        # 检查市场状态
                        current_weekday = datetime.now().weekday()
                        market_status = ""
                        
                        if price == 0 and prev_close > 0:
                            # 闭市状态，显示昨收价
                            if current_weekday >= 5:  # 周末
                                market_status = " [周五收盘]"
                            else:
                                market_status = " [闭市]"
                            return f"🏆 上海金: ¥{prev_close:.2f}/克{market_status}"
                        elif price > 0:
                            # 开市状态，显示实时价格
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"🏆 上海金: ¥{price:.2f}/克 {change_symbol}{change_pct:+.2f}%"
                        
            return "🏆 上海金: --"
    except Exception as e:
        logger.error(f"获取上海金价格失败: {e}")
        return "🏆 上海金: --"


async def get_btc_price():
    """获取BTC价格"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取BTC价格和涨跌幅
            url = "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD"
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
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"🪙 BTC: ${price:,.2f} {change_symbol}{change_pct:+.2f}%"
                return "🪙 BTC: --"
    except Exception as e:
        logger.error(f"获取BTC价格失败: {e}")
        return "🪙 BTC: --"


async def get_eth_price():
    """获取ETH价格"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取ETH价格和涨跌幅
            url = "https://query1.finance.yahoo.com/v8/finance/chart/ETH-USD"
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
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"💎 ETH: ${price:,.2f} {change_symbol}{change_pct:+.2f}%"
                return "💎 ETH: --"
    except Exception as e:
        logger.error(f"获取ETH价格失败: {e}")
        return "💎 ETH: --"


async def get_sse_index():
    """获取沪A大盘指数（上证指数）"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取上证指数 (代码: 000001.SS)
            url = "https://query1.finance.yahoo.com/v8/finance/chart/000001.SS"
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
                            
                            # 检查市场状态
                            market_state = meta.get('marketState', 'CLOSED')
                            current_weekday = datetime.now().weekday()
                            
                            market_status = ""
                            if current_weekday >= 5:  # 周末
                                market_status = " [周五收盘]"
                            elif market_state == 'CLOSED':
                                market_status = " [收盘]"
                            
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"📊 上证指数: {price:.2f}{market_status} {change_symbol}{change_value:+.2f} ({change_pct:+.2f}%)"
                        
                logger.warning("上证指数API返回数据格式异常")
                return "📊 上证指数: --"
    except asyncio.TimeoutError:
        logger.error("获取上证指数超时")
        return "📊 上证指数: 超时"
    except Exception as e:
        logger.error(f"获取上证指数失败: {e}")
        return "📊 上证指数: --"


async def get_nasdaq_index():
    """获取纳斯达克指数"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取纳斯达克指数 (代码: ^IXIC)
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC"
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
                            
                            # 检查市场状态
                            market_state = meta.get('marketState', 'CLOSED')
                            current_weekday = datetime.now().weekday()
                            
                            market_status = ""
                            if current_weekday >= 5:  # 周末
                                market_status = " [周五收盘]"
                            elif market_state == 'CLOSED':
                                market_status = " [收盘]"
                            
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"📊 纳斯达克: {price:,.2f}{market_status} {change_symbol}{change_value:+.2f} ({change_pct:+.2f}%)"
                        
                logger.warning("纳斯达克指数API返回数据格式异常")
                return "📊 纳斯达克: --"
    except asyncio.TimeoutError:
        logger.error("获取纳斯达克指数超时")
        return "📊 纳斯达克: 超时"
    except Exception as e:
        logger.error(f"获取纳斯达克指数失败: {e}")
        return "📊 纳斯达克: --"


async def get_dow_jones_index():
    """获取道琼斯指数"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取道琼斯指数 (代码: ^DJI)
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EDJI"
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
                            
                            # 检查市场状态
                            market_state = meta.get('marketState', 'CLOSED')
                            current_weekday = datetime.now().weekday()
                            
                            market_status = ""
                            if current_weekday >= 5:  # 周末
                                market_status = " [周五收盘]"
                            elif market_state == 'CLOSED':
                                market_status = " [收盘]"
                            
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"📊 道琼斯: {price:,.2f}{market_status} {change_symbol}{change_value:+.2f} ({change_pct:+.2f}%)"
                        
                logger.warning("道琼斯指数API返回数据格式异常")
                return "📊 道琼斯: --"
    except asyncio.TimeoutError:
        logger.error("获取道琼斯指数超时")
        return "📊 道琼斯: 超时"
    except Exception as e:
        logger.error(f"获取道琼斯指数失败: {e}")
        return "📊 道琼斯: --"


async def get_hsi_index():
    """获取香港恒生指数"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取恒生指数 (代码: ^HSI)
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EHSI"
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
                            
                            # 检查市场状态
                            market_state = meta.get('marketState', 'CLOSED')
                            current_weekday = datetime.now().weekday()
                            
                            market_status = ""
                            if current_weekday >= 5:  # 周末
                                market_status = " [周五收盘]"
                            elif market_state == 'CLOSED':
                                market_status = " [收盘]"
                            
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"📊 恒生指数: {price:,.2f}{market_status} {change_symbol}{change_value:+.2f} ({change_pct:+.2f}%)"
                        
                logger.warning("恒生指数API返回数据格式异常")
                return "📊 恒生指数: --"
    except asyncio.TimeoutError:
        logger.error("获取恒生指数超时")
        return "📊 恒生指数: 超时"
    except Exception as e:
        logger.error(f"获取恒生指数失败: {e}")
        return "📊 恒生指数: --"


async def send_price_update():
    """发送价格更新消息"""
    try:
        # 获取所有价格信息
        gold, shanghai_gold, dollar, usdcny, oil, btc, eth, sse, nasdaq, dow, hsi = await asyncio.gather(
            get_gold_price(),
            get_shanghai_gold_price(),
            get_dollar_index(),
            get_usdcny_rate(),
            get_oil_price(),
            get_btc_price(),
            get_eth_price(),
            get_sse_index(),
            get_nasdaq_index(),
            get_dow_jones_index(),
            get_hsi_index()
        )
        
        # 构建消息
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
📊 <b>金融市场价格更新</b>

{sse}
{btc}
{eth}
{gold}
{shanghai_gold}
{dollar}
{usdcny}
{oil}
{nasdaq}
{dow}
{hsi}

🕐 更新时间: {current_time}
        """.strip()
        
        # 发送消息
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='HTML'
        )
        logger.info(f"消息发送成功: {current_time}")
        
    except TelegramError as e:
        logger.error(f"发送消息失败: {e}")
    except Exception as e:
        logger.error(f"发生错误: {e}")


async def get_financial_news():
    """从金十数据获取财经快讯"""
    try:
        async with aiohttp.ClientSession() as session:
            # 直接解析金十数据网页HTML
            url = "https://www.jin10.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            try:
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        import re
                        
                        # 提取flash-text中的新闻内容
                        flash_pattern = r'class="flash-text">([^<]+(?:<[^>]+>[^<]+)*)</div>'
                        matches = re.findall(flash_pattern, html)
                        
                        # 过滤关键词
                        keywords = ['金价', '黄金', '美元', '原油', 'WTI', '布伦特', '比特币', 'BTC', 
                                   '以太坊', 'ETH', '上证', '纳斯达克', '道琼斯', '恒生', '股市', 
                                   '加密货币', '外汇', '人民币', 'CNY', '美联储', 'Fed', '央行',
                                   '通胀', 'CPI', 'GDP', '利率', '美债', '大盘', '指数', 
                                   '涨', '跌', '市场', '金银']
                        
                        news_list = []
                        for match in matches:
                            # 去除HTML标签
                            clean_text = re.sub(r'<[^>]+>', '', match)
                            # 去除多余空格
                            clean_text = ' '.join(clean_text.split())
                            
                            # 过滤VIP快讯
                            if 'VIP' in clean_text or '解锁' in clean_text:
                                continue
                            
                            # 检查是否包含关键词
                            if any(keyword in clean_text for keyword in keywords):
                                news_list.append(clean_text)
                        
                        if len(news_list) >= 5:
                            logger.info(f"从金十数据网页成功获取 {len(news_list)} 条新闻")
                            return news_list[:15]
            except Exception as e:
                logger.error(f"解析金十数据网页失败: {e}")
            
            # 备用方案: 从东方财富网获取并过滤
            url2 = "https://finance.eastmoney.com/"
            headers2 = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with session.get(url2, headers=headers2, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    import re
                    
                    # 提取新闻标题
                    pattern = r'<a[^>]+title="([^"]+)"[^>]*>(?:[^<]+)</a>'
                    matches = re.findall(pattern, html)
                    
                    if matches:
                        # 过滤与市场相关的新闻
                        keywords = ['黄金', '美元', '原油', '比特币', '以太坊', '上证', '纳指', 
                                   '道指', '恒生', '股市', '外汇', '人民币', '美联储', '央行',
                                   '通胀', 'CPI', 'GDP', '利率', '债券', '加密', '币', '金价']
                        
                        filtered_news = []
                        for news in matches:
                            if any(keyword in news for keyword in keywords):
                                filtered_news.append(news)
                        
                        if len(filtered_news) >= 5:
                            return filtered_news[:12]
                        else:
                            return matches[:10]
            
            return []
    except Exception as e:
        logger.error(f"获取财经新闻失败: {e}")
        return []


async def generate_news_brief():
    """生成财经新闻简报并发送"""
    try:
        # 获取新闻
        news_list = await get_financial_news()
        
        if not news_list:
            logger.warning("未能获取到财经新闻")
            return
        
        # 去重
        news_list = list(dict.fromkeys(news_list))
        
        # 构建简报内容
        if config.AI_ENABLED and len(news_list) >= 3:
            # 使用AI提炼要点（限制新闻数量）
            news_for_ai = news_list[:6]
            news_text = "\n".join(news_for_ai)
            
            prompt = f"""请用100字以内总结以下财经要闻的核心信息：

{news_text}

要求：1行话简洁 2客观中立 3突出市场动态"""
            
            try:
                response = await asyncio.to_thread(
                    gemini_model.generate_content,
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.5,
                        max_output_tokens=400,
                    ),
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                )
                ai_brief = response.text.strip()
                
                # 检查AI生成的内容是否有效
                if len(ai_brief) >= 40:
                    brief = f"<b>市场要点</b>\n{ai_brief}\n\n<b>重点资讯</b>\n" + "\n".join(f"• {news}" for news in news_list[:5])
                else:
                    # AI生成内容太短，使用列表形式
                    brief = "\n".join(f"• {news}" for news in news_list[:8])
                    
            except Exception as e:
                logger.error(f"AI生成简报失败: {e}")
                # 降级方案：直接列出新闻
                brief = "\n".join(f"• {news}" for news in news_list[:8])
        else:
            # AI未启用或新闻太少，直接列出新闻
            brief = "\n".join(f"• {news}" for news in news_list[:8])
        
        # 构建消息
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"""
📰 <b>财经市场简报</b>

{brief}

🕐 {current_time}
        """.strip()
        
        # 发送消息
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='HTML'
        )
        logger.info(f"财经简报发送成功: {current_time}")
        
    except TelegramError as e:
        logger.error(f"发送财经简报失败: {e}")
    except Exception as e:
        logger.error(f"生成财经简报时发生错误: {e}")


async def get_financial_calendar():
    """获取今日财经日历"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用金十数据API获取财经日历
            url = "https://rili.jin10.com/data/daily_events"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://rili.jin10.com/',
            }
            
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # 提取重要事件（importance >= 2）
                    events = []
                    if isinstance(data, list):
                        for item in data:
                            importance = item.get('star', 0)
                            if importance >= 2:  # 只获取重要事件
                                time = item.get('pub_time', '')
                                country = item.get('country', '')
                                event_name = item.get('name', '')
                                unit = item.get('unit', '')
                                previous = item.get('previous', '')
                                forecast = item.get('consensus', '')
                                
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
                        logger.info(f"获取到 {len(events)} 条财经日历事件")
                        return events
                    
            # 备用方案：从英为财情获取
            url2 = "https://cn.investing.com/economic-calendar/"
            headers2 = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
            
            async with session.get(url2, headers=headers2, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    import re
                    from bs4 import BeautifulSoup
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    events = []
                    
                    # 查找今日事件行
                    rows = soup.find_all('tr', {'class': re.compile(r'event')})
                    for row in rows[:15]:  # 限制数量
                        try:
                            time_elem = row.find('td', {'class': 'time'})
                            event_elem = row.find('td', {'class': 'event'})
                            importance_elem = row.find('td', {'class': 'sentiment'})
                            
                            if time_elem and event_elem:
                                time = time_elem.get_text(strip=True)
                                event_name = event_elem.get_text(strip=True)
                                
                                # 判断重要性（通过bull图标数量）
                                bulls = importance_elem.find_all('i', {'class': 'grayFullBullishIcon'}) if importance_elem else []
                                importance = len(bulls)
                                
                                if importance >= 2:  # 只获取重要事件
                                    events.append({
                                        'time': time,
                                        'info': f"{time} {event_name}",
                                        'importance': importance
                                    })
                        except Exception as e:
                            continue
                    
                    if events:
                        logger.info(f"从备用源获取到 {len(events)} 条财经日历事件")
                        return events
            
            logger.warning("未能获取到财经日历数据")
            return []
            
    except Exception as e:
        logger.error(f"获取财经日历失败: {e}")
        return []


async def send_financial_calendar():
    """发送今日财经日历"""
    try:
        events = await get_financial_calendar()
        
        if not events:
            logger.warning("未获取到财经日历数据，跳过推送")
            return
        
        # 构建消息
        current_date = datetime.now().strftime('%Y年%m月%d日')
        message = f"📅 <b>{current_date} 财经日历</b>\n\n"
        message += "<b>今日重要事件：</b>\n\n"
        
        for event in events[:12]:  # 限制显示数量
            importance = event['importance']
            stars = '⭐' * importance
            message += f"{stars} {event['info']}\n"
        
        if len(events) > 12:
            message += f"\n... 还有 {len(events) - 12} 个其他事件"
        
        message += "\n\n💡 <i>请关注重要数据发布时间</i>"
        
        # 发送消息
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='HTML'
        )
        logger.info(f"财经日历发送成功: {current_date}")
        
    except TelegramError as e:
        logger.error(f"发送财经日历失败: {e}")
    except Exception as e:
        logger.error(f"生成财经日历时发生错误: {e}")


async def ask_ai(question: str) -> str:
    """使用Google Gemini回答问题"""
    if not config.AI_ENABLED:
        return "AI功能未启用"
    
    try:
        # 使用 Gemini 生成回答
        response = await asyncio.to_thread(
            gemini_model.generate_content,
            question,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=config.AI_MAX_TOKENS,
                temperature=config.AI_TEMPERATURE
            )
        )
        
        answer = response.text.strip()
        return answer
        
    except Exception as e:
        logger.error(f"AI回答失败 (模型: {config.GEMINI_MODEL}): {e}")
        # 如果是模型不存在的错误，提供更友好的提示
        if "404" in str(e) or "not found" in str(e).lower():
            return f"抱歉，AI模型配置错误。请检查config.py中的GEMINI_MODEL设置。\n推荐使用: gemini-1.5-flash 或 gemini-1.5-pro"
        return f"抱歉，AI回答时出现错误: {str(e)}"


async def handle_message(update: Update, context):
    """处理接收到的消息"""
    logger.info(f"收到消息更新: {update}")
    
    if not update.message or not update.message.text:
        logger.info("消息无文本内容，跳过")
        return
    
    message_text = update.message.text.strip()
    chat_id = update.message.chat_id
    
    logger.info(f"消息文本: {message_text}, 群组ID: {chat_id}, 配置的群组ID: {CHAT_ID}")
    
    # 只处理群组消息
    if str(chat_id) != CHAT_ID:
        logger.info(f"群组ID不匹配，跳过。收到: {chat_id}, 期望: {CHAT_ID}")
        return
    
    # 检查是否@机器人或回复机器人的消息
    bot_username = (await context.bot.get_me()).username
    logger.info(f"机器人用户名: {bot_username}")
    
    is_mentioned = f"@{bot_username}" in message_text
    is_reply_to_bot = (update.message.reply_to_message and 
                       update.message.reply_to_message.from_user.id == context.bot.id)
    
    logger.info(f"是否@机器人: {is_mentioned}, 是否回复机器人: {is_reply_to_bot}")
    
    if is_mentioned or is_reply_to_bot:
        # 移除@机器人的部分
        question = message_text.replace(f"@{bot_username}", "").strip()
        
        if not question:
            return
        
        logger.info(f"收到问题: {question}")
        
        # 发送"正在思考"的提示
        thinking_msg = await context.bot.send_message(
            chat_id=chat_id,
            text="🤔 正在思考...",
            reply_to_message_id=update.message.message_id
        )
        
        # 获取AI回答
        answer = await ask_ai(question)
        
        # 删除"正在思考"的消息
        try:
            await thinking_msg.delete()
        except:
            pass
        
        # 发送AI回答
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🤖 {answer}",
            reply_to_message_id=update.message.message_id
        )
        logger.info(f"已回复问题: {question[:50]}...")


async def start_command(update: Update, context):
    """处理/start命令"""
    await update.message.reply_text(
        "你好！我是金融价格机器人 + AI助手 🤖\n\n"
        "功能：\n"
        "1. 定时推送金融市场价格信息\n"
        "2. 在群里@我或回复我的消息来提问，我会用AI回答你的问题\n\n"
        "示例：@bot 今天天气怎么样？"
    )


async def help_command(update: Update, context):
    """处理/help命令"""
    await update.message.reply_text(
        "📖 使用说明：\n\n"
        "💰 自动推送价格信息\n"
        "机器人会在每天固定时间自动推送金融市场价格\n\n"
        "🤖 AI问答功能\n"
        "- 在群里@机器人 + 问题\n"
        "- 或者回复机器人的消息来提问\n\n"
        "示例：\n"
        "@bot 比特币是什么？\n"
        "@bot 如何理财？"
    )


async def main():
    """主函数"""
    logger.info("机器人启动中...")
    
    # 创建Application实例（用于接收消息）
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加消息处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 创建调度器
    scheduler = AsyncIOScheduler()
    
    # 添加定时任务 - 每天指定时间执行
    # 时间：07:30, 11:30, 15:00, 17:40, 20:00, 21:00, 22:00
    scheduler.add_job(
        send_price_update,
        CronTrigger(hour=7, minute=30),
        id='price_update_0730',
        name='早上7:30价格更新',
        replace_existing=True
    )
    scheduler.add_job(
        send_price_update,
        CronTrigger(hour=11, minute=30),
        id='price_update_1130',
        name='上午11:30价格更新',
        replace_existing=True
    )
    scheduler.add_job(
        send_price_update,
        CronTrigger(hour=15, minute=0),
        id='price_update_1500',
        name='下午15:00价格更新',
        replace_existing=True
    )
    scheduler.add_job(
        send_price_update,
        CronTrigger(hour=17, minute=40),
        id='price_update_1740',
        name='下午17:40价格更新',
        replace_existing=True
    )
    scheduler.add_job(
        send_price_update,
        CronTrigger(hour=20, minute=0),
        id='price_update_2000',
        name='晚上20:00价格更新',
        replace_existing=True
    )
    scheduler.add_job(
        send_price_update,
        CronTrigger(hour=21, minute=0),
        id='price_update_2100',
        name='晚上21:00价格更新',
        replace_existing=True
    )
    scheduler.add_job(
        send_price_update,
        CronTrigger(hour=22, minute=0),
        id='price_update_2200',
        name='晚上22:00价格更新',
        replace_existing=True
    )
    
    # 添加财经新闻简报定时任务（已暂停）
    # scheduler.add_job(
    #     generate_news_brief,
    #     CronTrigger(hour=9, minute=0),
    #     id='news_brief_0900',
    #     name='上午9:00财经简报',
    #     replace_existing=True
    # )
    # scheduler.add_job(
    #     generate_news_brief,
    #     CronTrigger(hour=17, minute=0),
    #     id='news_brief_1700',
    #     name='下午17:00财经简报',
    #     replace_existing=True
    # )
    # scheduler.add_job(
    #     generate_news_brief,
    #     CronTrigger(hour=23, minute=0),
    #     id='news_brief_2300',
    #     name='晚上23:00财经简报',
    #     replace_existing=True
    # )
    
    # 添加财经日历定时任务
    scheduler.add_job(
        send_financial_calendar,
        CronTrigger(hour=7, minute=0),
        id='calendar_0700',
        name='早上7:00财经日历',
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    logger.info("调度器已启动")
    
    # 立即发送一次测试消息
    await send_price_update()
    
    # 启动bot接收消息
    logger.info("启动消息接收...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    logger.info("机器人已启动，AI功能已" + ("启用" if config.AI_ENABLED else "禁用"))
    
    # 保持程序运行
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("正在关闭...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        scheduler.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
