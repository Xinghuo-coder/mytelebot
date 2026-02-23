#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试川普推特获取功能
"""

import asyncio
import aiohttp
import config

async def test_trump_tweets():
    """测试获取川普推文"""
    print("=" * 60)
    print("测试川普推特获取功能")
    print("=" * 60)
    
    tweets = []
    
    async with aiohttp.ClientSession() as session:
        # 测试每个Nitter实例
        for nitter_instance in config.TRUMP_NITTER_INSTANCES:
            print(f"\n测试 Nitter 实例: {nitter_instance}")
            try:
                url = f"{nitter_instance}/{config.TRUMP_TWITTER_USERNAME}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                
                print(f"请求 URL: {url}")
                async with session.get(url, headers=headers, timeout=10) as response:
                    print(f"响应状态码: {response.status}")
                    
                    if response.status == 200:
                        html = await response.text()
                        print(f"HTML 长度: {len(html)} 字符")
                        
                        import re
                        from html import unescape
                        
                        # 解析推文内容
                        tweet_pattern = r'<div class="tweet-content[^"]*"[^>]*>(.*?)</div>'
                        tweet_matches = re.findall(tweet_pattern, html, re.DOTALL)
                        
                        # 解析推文ID
                        tweet_link_pattern = r'href="/[^/]+/status/(\d+)"'
                        tweet_ids = re.findall(tweet_link_pattern, html)
                        
                        print(f"找到 {len(tweet_matches)} 个推文内容匹配")
                        print(f"找到 {len(tweet_ids)} 个推文ID")
                        
                        for i, (content, tweet_id) in enumerate(zip(tweet_matches[:3], tweet_ids[:3])):
                            # 清理HTML标签
                            clean_content = re.sub(r'<[^>]+>', '', content)
                            clean_content = unescape(clean_content).strip()
                            
                            # 跳过转发和回复
                            if clean_content.startswith('RT @') or clean_content.startswith('@'):
                                print(f"  推文 {i+1}: [跳过 - 转发或回复]")
                                continue
                            
                            tweets.append({
                                'id': tweet_id,
                                'content': clean_content[:100] + '...' if len(clean_content) > 100 else clean_content,
                                'url': f"https://twitter.com/{config.TRUMP_TWITTER_USERNAME}/status/{tweet_id}"
                            })
                            
                            print(f"  推文 {i+1} ID: {tweet_id}")
                            print(f"  内容预览: {clean_content[:80]}...")
                        
                        if tweets:
                            print(f"\n✅ 成功！从 {nitter_instance} 获取到 {len(tweets)} 条推文")
                            break
                    else:
                        print(f"❌ HTTP 状态码错误: {response.status}")
                        
            except asyncio.TimeoutError:
                print(f"❌ 超时")
            except Exception as e:
                print(f"❌ 错误: {e}")
        
        # 测试 RSS Bridge
        if not tweets:
            print("\n" + "=" * 60)
            print("尝试 RSS Bridge")
            print("=" * 60)
            
            rss_instances = [
                f"https://rss-bridge.org/bridge01/?action=display&bridge=Twitter&context=By+username&u={config.TRUMP_TWITTER_USERNAME}&format=Json",
                f"https://wtf.roflcopter.fr/rss-bridge/?action=display&bridge=Twitter&context=By+username&u={config.TRUMP_TWITTER_USERNAME}&format=Json",
            ]
            
            for rss_url in rss_instances:
                try:
                    print(f"\n测试 RSS Bridge: {rss_url}")
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    
                    async with session.get(rss_url, headers=headers, timeout=15) as response:
                        print(f"响应状态码: {response.status}")
                        
                        if response.status == 200:
                            data = await response.json()
                            print(f"JSON 数据键: {list(data.keys())}")
                            
                            if 'items' in data:
                                print(f"包含 {len(data['items'])} 条推文")
                                
                                for i, item in enumerate(data['items'][:3]):
                                    url = item.get('url', '')
                                    tweet_id = url.split('/')[-1] if url else ''
                                    content = item.get('content_text', '') or item.get('title', '')
                                    date = item.get('date_published', '')
                                    
                                    if content.startswith('RT @'):
                                        print(f"  推文 {i+1}: [跳过 - 转发]")
                                        continue
                                    
                                    tweets.append({
                                        'id': tweet_id,
                                        'content': content[:100] + '...' if len(content) > 100 else content,
                                        'time': date,
                                        'url': url
                                    })
                                    
                                    print(f"  推文 {i+1} ID: {tweet_id}")
                                    print(f"  内容预览: {content[:80]}...")
                                    print(f"  发布时间: {date}")
                                
                                if tweets:
                                    print(f"\n✅ 成功！从 RSS Bridge 获取到 {len(tweets)} 条推文")
                                    break
                        
                except Exception as e:
                    print(f"❌ 错误: {e}")
        
        # 测试 Syndication API
        if not tweets:
            print("\n" + "=" * 60)
            print("尝试 Twitter Syndication API")
            print("=" * 60)
            
            try:
                api_url = f"https://cdn.syndication.twimg.com/timeline/profile?screen_name={config.TRUMP_TWITTER_USERNAME}&count=5"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'application/json'
                }
                
                print(f"请求 URL: {api_url}")
                async with session.get(api_url, headers=headers, timeout=10) as response:
                    print(f"响应状态码: {response.status}")
                    content_type = response.headers.get('content-type', '')
                    print(f"Content-Type: {content_type}")
                    
                    if response.status == 200:
                        try:
                            if 'json' in content_type.lower():
                                data = await response.json()
                            else:
                                text = await response.text()
                                import json
                                data = json.loads(text)
                            
                            print(f"JSON 数据键: {list(data.keys())}")
                            
                            if 'timeline' in data:
                                print(f"时间线包含 {len(data['timeline'])} 条推文")
                                
                                for i, tweet_data in enumerate(data['timeline'][:3]):
                                    tweet_id = tweet_data.get('id_str', '')
                                    content = tweet_data.get('text', '')
                                    created_at = tweet_data.get('created_at', '')
                                    
                                    if content.startswith('RT @'):
                                        print(f"  推文 {i+1}: [跳过 - 转发]")
                                        continue
                                    
                                    tweets.append({
                                        'id': tweet_id,
                                        'content': content[:100] + '...' if len(content) > 100 else content,
                                        'time': created_at
                                    })
                                    
                                    print(f"  推文 {i+1} ID: {tweet_id}")
                                    print(f"  内容预览: {content[:80]}...")
                                    print(f"  发布时间: {created_at}")
                                
                                if tweets:
                                    print(f"\n✅ 成功！从 Syndication API 获取到 {len(tweets)} 条推文")
                        except Exception as e:
                            print(f"❌ 解析响应失败: {e}")
                    else:
                        print(f"❌ HTTP 状态码错误: {response.status}")
                        
            except Exception as e:
                print(f"❌ 错误: {e}")
    
    # 输出最终结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    if tweets:
        print(f"✅ 成功获取到 {len(tweets)} 条推文\n")
        for i, tweet in enumerate(tweets, 1):
            print(f"{i}. ID: {tweet['id']}")
            print(f"   内容: {tweet['content']}")
            if 'url' in tweet:
                print(f"   链接: {tweet['url']}")
            if 'time' in tweet:
                print(f"   时间: {tweet['time']}")
            print()
    else:
        print("❌ 未能获取到任何推文")
        print("\n可能的原因：")
        print("1. 所有 Nitter 实例都不可用")
        print("2. Twitter API 限流")
        print("3. 网络连接问题")
        print("4. 用户名错误或账号被封禁")
        print("\n建议：")
        print("1. 检查网络连接")
        print("2. 尝试在浏览器中访问 Nitter 实例")
        print("3. 在 config.py 中添加更多 Nitter 镜像站")


if __name__ == '__main__':
    asyncio.run(test_trump_tweets())
