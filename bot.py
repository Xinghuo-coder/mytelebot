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
import json
import os

# Twitter API (tweepy)
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    if config.TRUMP_TWITTER_ENABLED and config.TWITTER_USE_OFFICIAL_API:
        logger.warning("tweepy未安装，请运行: pip install tweepy")

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

# 川普推特监控 - 存储已发送的推文ID
SENT_TWEETS_FILE = "sent_tweets.json"
sent_tweet_ids = set()

def load_sent_tweets():
    """从文件加载已发送的推文ID"""
    global sent_tweet_ids
    try:
        if os.path.exists(SENT_TWEETS_FILE):
            with open(SENT_TWEETS_FILE, 'r') as f:
                sent_tweet_ids = set(json.load(f))
                logger.info(f"已加载 {len(sent_tweet_ids)} 个已发送推文ID")
    except Exception as e:
        logger.error(f"加载已发送推文ID失败: {e}")
        sent_tweet_ids = set()

def save_sent_tweets():
    """保存已发送的推文ID到文件"""
    try:
        # 只保留最近100个ID，避免文件过大
        tweets_to_save = list(sent_tweet_ids)[-100:]
        with open(SENT_TWEETS_FILE, 'w') as f:
            json.dump(tweets_to_save, f)
    except Exception as e:
        logger.error(f"保存已发送推文ID失败: {e}")


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


async def get_trump_tweets():
    """获取指定用户的最新推文"""
    if not config.TRUMP_TWITTER_ENABLED:
        return []
    
    tweets = []
    
    # 优先使用官方API
    if config.TWITTER_USE_OFFICIAL_API and TWEEPY_AVAILABLE:
        try:
            # 使用Twitter API V2 (免费层级可用)
            client = tweepy.Client(
                consumer_key=config.TWITTER_API_KEY,
                consumer_secret=config.TWITTER_API_SECRET,
                access_token=config.TWITTER_ACCESS_TOKEN,
                access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET
            )
            
            # 获取用户ID
            user = client.get_user(username=config.TRUMP_TWITTER_USERNAME)
            if not user.data:
                logger.error(f"用户 @{config.TRUMP_TWITTER_USERNAME} 不存在")
                return []
            
            user_id = user.data.id
            
            # 获取用户最新推文 (使用API V2)
            tweets_response = client.get_users_tweets(
                id=user_id,
                max_results=5,
                exclude=['retweets', 'replies'],
                tweet_fields=['created_at', 'text']
            )
            
            if tweets_response.data:
                for tweet in tweets_response.data:
                    tweets.append({
                        'id': str(tweet.id),
                        'content': tweet.text,
                        'time': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S') if tweet.created_at else '',
                        'url': f"https://twitter.com/{config.TRUMP_TWITTER_USERNAME}/status/{tweet.id}"
                    })
                
                logger.info(f"从Twitter API V2获取到 {len(tweets)} 条推文")
                return tweets
            else:
                logger.warning(f"用户 @{config.TRUMP_TWITTER_USERNAME} 暂无推文")
                return []
                
        except Exception as e:
            logger.error(f"Twitter官方API获取失败: {e}")
            logger.info("尝试使用备用方案...")
    
    # 备用方案：使用第三方服务
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            # 方法1: 尝试使用 Nitter (Twitter的开源前端)
            for nitter_instance in config.TRUMP_NITTER_INSTANCES:
                try:
                    url = f"{nitter_instance}/{config.TRUMP_TWITTER_USERNAME}"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    
                    async with session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            import re
                            from html import unescape
                            
                            # 解析推文内容
                            # Nitter的HTML结构：推文在 <div class="tweet-content"> 中
                            tweet_pattern = r'<div class="tweet-content[^"]*"[^>]*>(.*?)</div>'
                            tweet_matches = re.findall(tweet_pattern, html, re.DOTALL)
                            
                            # 解析推文ID和时间
                            tweet_link_pattern = r'href="/[^/]+/status/(\d+)"'
                            tweet_ids = re.findall(tweet_link_pattern, html)
                            
                            # 解析时间
                            time_pattern = r'<span class="tweet-date"[^>]*title="([^"]+)"'
                            times = re.findall(time_pattern, html)
                            
                            for i, (content, tweet_id) in enumerate(zip(tweet_matches[:5], tweet_ids[:5])):
                                # 清理HTML标签
                                clean_content = re.sub(r'<[^>]+>', '', content)
                                clean_content = unescape(clean_content).strip()
                                
                                # 跳过转发和回复
                                if clean_content.startswith('RT @') or clean_content.startswith('@'):
                                    continue
                                
                                tweet_time = times[i] if i < len(times) else "未知时间"
                                
                                tweets.append({
                                    'id': tweet_id,
                                    'content': clean_content,
                                    'time': tweet_time,
                                    'url': f"https://twitter.com/{config.TRUMP_TWITTER_USERNAME}/status/{tweet_id}"
                                })
                            
                            if tweets:
                                logger.info(f"从 {nitter_instance} 获取到 {len(tweets)} 条推文")
                                return tweets
                            
                except Exception as e:
                    logger.warning(f"从 {nitter_instance} 获取推文失败: {e}")
                    continue
            
            # 方法2: 使用 Twitter API (需要API密钥)
            # 这里可以添加Twitter API的实现，但需要用户自己申请API密钥
            
            # 方法3: 使用 RSS Bridge (更可靠的备选方案)
            try:
                # 尝试使用 RSS Bridge
                rss_instances = [
                    f"https://rss-bridge.org/bridge01/?action=display&bridge=Twitter&context=By+username&u={config.TRUMP_TWITTER_USERNAME}&format=Json",
                    f"https://wtf.roflcopter.fr/rss-bridge/?action=display&bridge=Twitter&context=By+username&u={config.TRUMP_TWITTER_USERNAME}&format=Json",
                ]
                
                for rss_url in rss_instances:
                    try:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                        }
                        
                        async with session.get(rss_url, headers=headers, timeout=10) as response:
                            if response.status == 200:
                                try:
                                    data = await response.json()
                                    
                                    if 'items' in data:
                                        for item in data['items'][:5]:
                                            # 从URL提取推文ID
                                            url = item.get('url', '')
                                            tweet_id = url.split('/')[-1] if url else ''
                                            content = item.get('content_text', '') or item.get('title', '')
                                            date = item.get('date_published', '')
                                            
                                            # 跳过转发
                                            if content.startswith('RT @'):
                                                continue
                                            
                                            tweets.append({
                                                'id': tweet_id,
                                                'content': content,
                                                'time': date,
                                                'url': url
                                            })
                                        
                                        if tweets:
                                            logger.info(f"从 RSS Bridge 获取到 {len(tweets)} 条推文")
                                            return tweets
                                except Exception as e:
                                    logger.warning(f"解析RSS数据失败: {e}")
                                    continue
                    except Exception as e:
                        logger.warning(f"从 {rss_url} 获取失败: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"RSS Bridge 方法失败: {e}")
            
            # 方法4: 使用 Syndication API (作为最后备选)
            try:
                api_url = f"https://cdn.syndication.twimg.com/timeline/profile?screen_name={config.TRUMP_TWITTER_USERNAME}&count=5"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'application/json'
                }
                
                async with session.get(api_url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        # 尝试解析JSON
                        if 'json' in content_type.lower():
                            data = await response.json()
                        else:
                            # 尝试强制解析为JSON
                            text = await response.text()
                            import json
                            data = json.loads(text)
                        
                        if 'timeline' in data:
                            for tweet_data in data['timeline'][:5]:
                                tweet_id = tweet_data.get('id_str', '')
                                content = tweet_data.get('text', '')
                                created_at = tweet_data.get('created_at', '')
                                
                                if content.startswith('RT @'):
                                    continue
                                
                                tweets.append({
                                    'id': tweet_id,
                                    'content': content,
                                    'time': created_at,
                                    'url': f"https://twitter.com/{config.TRUMP_TWITTER_USERNAME}/status/{tweet_id}"
                                })
                            
                            if tweets:
                                logger.info(f"从 Syndication API 获取到 {len(tweets)} 条推文")
                                return tweets
                                
            except Exception as e:
                logger.warning(f"从 Syndication API 获取推文失败: {e}")
            
            # 如果所有方法都失败
            logger.warning("所有获取推文的方法都失败了")
            return []
            
    except Exception as e:
        logger.error(f"获取川普推文失败: {e}")
        return []


async def check_and_send_trump_tweets():
    """检查并发送川普的新推文"""
    if not config.TRUMP_TWITTER_ENABLED:
        return
    
    try:
        logger.info("开始检查川普推特...")
        tweets = await get_trump_tweets()
        
        if not tweets:
            logger.info("未获取到新推文")
            return
        
        new_tweets_sent = 0
        
        # 倒序处理推文，先发旧的
        for tweet in reversed(tweets):
            tweet_id = tweet['id']
            
            # 检查是否已发送
            if tweet_id in sent_tweet_ids:
                continue
            
            # 构建消息
            username_display = config.TRUMP_TWITTER_USERNAME
            message = f"""
🐦 <b>@{username_display} 推特更新</b>

{tweet['content']}

🔗 <a href="{tweet['url']}">查看原推文</a>
🕐 {tweet['time']}
            """.strip()
            
            try:
                # 发送消息
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
                
                # 记录已发送
                sent_tweet_ids.add(tweet_id)
                save_sent_tweets()
                new_tweets_sent += 1
                
                logger.info(f"✅ 成功发送推文 @{config.TRUMP_TWITTER_USERNAME} ID: {tweet_id}")
                
                # 避免发送太快
                await asyncio.sleep(2)
                
            except TelegramError as e:
                logger.error(f"发送川普推文失败: {e}")
                # 即使发送失败，也标记为已处理，避免重复尝试
                sent_tweet_ids.add(tweet_id)
                save_sent_tweets()
        
        if new_tweets_sent > 0:
            logger.info(f"✅ 共发送了 {new_tweets_sent} 条新推文")
        else:
            logger.info("没有新推文需要发送")
            
    except Exception as e:
        logger.error(f"检查川普推文时发生错误: {e}")


async def get_sse_index():
    """获取沪A大盘指数（上证指数）- 使用东方财富网API"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用东方财富网API获取上证指数
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'secid': '1.000001',  # 上证指数
                'fields': 'f43,f44,f45,f46,f57,f58,f60,f170',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://quote.eastmoney.com/'
            }
            
            async with session.get(url, params=params, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('data'):
                        quote = data['data']
                        
                        # 东方财富网价格字段说明:
                        # f43: 最新价 (单位: 分，需要除以100)
                        # f60: 昨收价 (单位: 分，需要除以100)
                        # f170: 涨跌幅百分比 (单位: 百分点的100倍，需要除以100)
                        price = quote.get('f43', 0)  # 最新价
                        prev_close = quote.get('f60', 0)  # 昨收
                        change_pct = quote.get('f170', 0)  # 涨跌幅
                        
                        if price > 0 and prev_close > 0:
                            # 价格需要除以100转换为点数
                            price = price / 100
                            prev_close = prev_close / 100
                            # 涨跌幅需要除以100转换为百分比
                            change_pct = change_pct / 100
                            change_value = price - prev_close
                            
                            # 检查市场状态
                            current_weekday = datetime.now().weekday()
                            current_hour = datetime.now().hour
                            
                            market_status = ""
                            # 交易日：周一至周五
                            # 交易时间：9:30-11:30, 13:00-15:00
                            if current_weekday >= 5:  # 周末
                                market_status = " [周五收盘]"
                            elif current_hour < 9 or (current_hour == 9 and datetime.now().minute < 30):
                                market_status = " [未开盘]"
                            elif (current_hour >= 11 and current_hour < 13) or (current_hour == 11 and datetime.now().minute >= 30):
                                market_status = " [午间休市]"
                            elif current_hour >= 15:
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


async def get_hstech_index():
    """获取恒生科技指数"""
    try:
        async with aiohttp.ClientSession() as session:
            # 使用Yahoo Finance获取恒生科技指数 (代码: HSTECH.HK)
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
                            
                            # 检查市场状态
                            market_state = meta.get('marketState', 'CLOSED')
                            current_weekday = datetime.now().weekday()
                            
                            market_status = ""
                            if current_weekday >= 5:  # 周末
                                market_status = " [周五收盘]"
                            elif market_state == 'CLOSED':
                                market_status = " [收盘]"
                            
                            change_symbol = "📈" if change_pct >= 0 else "📉"
                            return f"🔬 恒生科技: {price:,.2f}{market_status} {change_symbol}{change_value:+.2f} ({change_pct:+.2f}%)"
                        
                logger.warning("恒生科技指数API返回数据格式异常")
                return "🔬 恒生科技: --"
    except asyncio.TimeoutError:
        logger.error("获取恒生科技指数超时")
        return "🔬 恒生科技: 超时"
    except Exception as e:
        logger.error(f"获取恒生科技指数失败: {e}")
        return "🔬 恒生科技: --"


async def send_price_update():
    """发送价格更新消息"""
    try:
        # 获取所有价格信息
        gold, shanghai_gold, dollar, usdcny, oil, btc, eth, sse, nasdaq, dow, hsi, hstech = await asyncio.gather(
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
            get_hsi_index(),
            get_hstech_index()
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
{hstech}

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
        
        # 尝试从多个数据源获取实时数据
        async with aiohttp.ClientSession() as session:
            # 简化方案：使用模拟数据配合每周固定事件
            events = []
            
            # 添加今日固定事件
            fixed_events = weekday_events.get(today_weekday, [])
            for event in fixed_events:
                if event not in ["无固定重要事件", "休市日"]:
                    events.append({
                        'time': event.split()[1] if len(event.split()) > 1 else '待定',
                        'info': event,
                        'importance': 3 if '⭐⭐⭐' in event else 2
                    })
            
            # 添加常规性重要事件提醒
            current_day = datetime.now().day
            
            # 每月初（1-5号）提醒重要数据发布日
            if 1 <= current_day <= 5:
                events.append({
                    'time': '本周',
                    'info': '⭐⭐⭐ 本周关注：美国非农就业、中国CPI/PPI数据发布',
                    'importance': 3
                })
            
            # 美联储决议周（通常每月中下旬）
            if 15 <= current_day <= 20:
                events.append({
                    'time': '本月',
                    'info': '⭐⭐⭐ 本月关注：美联储利率决议（FOMC会议）',
                    'importance': 3
                })
            
            # 如果是周五，特别提醒非农
            if today_weekday == 4 and 1 <= current_day <= 7:
                events.append({
                    'time': '20:30',
                    'info': '⭐⭐⭐ 20:30 🇺🇸 美国非农就业数据 (本月首个周五)',
                    'importance': 3
                })
            
            if events:
                logger.info(f"生成财经日历提醒 {len(events)} 条")
                return events
            
            # 如果是周末，返回休市提示
            if today_weekday >= 5:
                return [{
                    'time': '全天',
                    'info': '📅 今日市场休市',
                    'importance': 1
                }]
            
            # 默认返回一些通用提醒
            return [{
                'time': '全天',
                'info': '📊 今日关注：主要货币汇率、贵金属价格、原油价格波动',
                'importance': 2
            }]
            
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
    trump_status = "✅ 已启用" if config.TRUMP_TWITTER_ENABLED else "❌ 未启用"
    await update.message.reply_text(
        "你好！我是金融价格机器人 + AI助手 🤖\n\n"
        "功能：\n"
        "1. 定时推送金融市场价格信息\n"
        "2. 实时监控川普推特并推送 " + trump_status + "\n"
        "3. 在群里@我或回复我的消息来提问，我会用AI回答你的问题\n\n"
        "示例：@bot 今天天气怎么样？"
    )


async def help_command(update: Update, context):
    """处理/help命令"""
    trump_info = ""
    if config.TRUMP_TWITTER_ENABLED:
        trump_info = f"\n\n🐦 <b>川普推特监控</b>\n每{config.TRUMP_CHECK_INTERVAL}分钟自动检查川普推特\n发现新推文将立即推送到群里"
    
    await update.message.reply_text(
        "📖 <b>使用说明：</b>\n\n"
        "💰 <b>自动推送价格信息</b>\n"
        "机器人会在每天固定时间自动推送金融市场价格"
        + trump_info +
        "\n\n🤖 <b>AI问答功能</b>\n"
        "- 在群里@机器人 + 问题\n"
        "- 或者回复机器人的消息来提问\n\n"
        "<b>示例：</b>\n"
        "@bot 比特币是什么？\n"
        "@bot 如何理财？",
        parse_mode='HTML'
    )


async def main():
    """主函数"""
    logger.info("机器人启动中...")
    
    # 加载已发送的推文ID
    load_sent_tweets()
    
    # 创建Application实例（用于接收消息）
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加消息处理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 创建调度器
    scheduler = AsyncIOScheduler()
    
    # 添加定时任务 - 根据config.py配置动态添加
    # 从配置文件读取定时任务时间
    for hour in config.SCHEDULE_HOURS:
        minute = config.SCHEDULE_MINUTES.get(hour, 0)  # 如果没有特殊分钟数，默认为整点
        time_str = f"{hour:02d}:{minute:02d}"
        scheduler.add_job(
            send_price_update,
            CronTrigger(hour=hour, minute=minute),
            id=f'price_update_{hour:02d}{minute:02d}',
            name=f'{time_str}价格更新',
            replace_existing=True
        )
        logger.info(f"已添加定时任务: {time_str}价格更新")
    
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
    
    # 添加财经日历定时任务 - 从配置文件读取
    for hour in config.CALENDAR_HOURS:
        minute = config.CALENDAR_MINUTES.get(hour, 0)
        time_str = f"{hour:02d}:{minute:02d}"
        time_label = "早上" if hour < 12 else "下午" if hour < 18 else "晚上"
        scheduler.add_job(
            send_financial_calendar,
            CronTrigger(hour=hour, minute=minute),
            id=f'calendar_{hour:02d}{minute:02d}',
            name=f'{time_label}{time_str}财经日历',
            replace_existing=True
        )
        logger.info(f"已添加财经日历任务: {time_label}{time_str}")
    
    # 添加川普推特监控定时任务
    if config.TRUMP_TWITTER_ENABLED:
        from apscheduler.triggers.interval import IntervalTrigger
        scheduler.add_job(
            check_and_send_trump_tweets,
            IntervalTrigger(minutes=config.TRUMP_CHECK_INTERVAL),
            id='trump_twitter_check',
            name=f'每{config.TRUMP_CHECK_INTERVAL}分钟检查川普推特',
            replace_existing=True
        )
        logger.info(f"川普推特监控已启用，每{config.TRUMP_CHECK_INTERVAL}分钟检查一次")
    
    # 启动调度器
    scheduler.start()
    logger.info("调度器已启动")
    
    # 立即发送一次测试消息
    await send_price_update()
    
    # 立即检查一次川普推特（如果启用）
    if config.TRUMP_TWITTER_ENABLED:
        logger.info("立即检查川普推特...")
        await check_and_send_trump_tweets()
    
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
