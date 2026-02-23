#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Twitter官方API配置
"""

import sys

print("=" * 60)
print("Twitter API 配置测试")
print("=" * 60)

# 检查tweepy是否安装
print("\n1. 检查 tweepy 库...")
try:
    import tweepy
    print("✅ tweepy 已安装")
except ImportError:
    print("❌ tweepy 未安装")
    print("\n请运行: pip install tweepy")
    sys.exit(1)

# 加载配置
print("\n2. 加载配置文件...")
try:
    import config
    print("✅ config.py 加载成功")
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    sys.exit(1)

# 检查配置
print("\n3. 检查配置项...")
required_configs = [
    'TWITTER_API_KEY',
    'TWITTER_API_SECRET',
    'TWITTER_ACCESS_TOKEN',
    'TWITTER_ACCESS_TOKEN_SECRET',
    'TRUMP_TWITTER_USERNAME'
]

missing = []
placeholder_values = ['你的API_Key', '你的API_Secret', '你的Access_Token', '你的Access_Token_Secret']
for key in required_configs:
    if not hasattr(config, key):
        missing.append(key)
        print(f"❌ 缺少配置: {key}")
    else:
        value = getattr(config, key)
        if not value or value in placeholder_values:
            print(f"⚠️  {key} 需要替换为真实密钥")
            missing.append(key)
        else:
            print(f"✅ {key}: {str(value)[:10]}...")

if missing:
    print("\n❌ 请先在 config.py 中配置以上密钥")
    print("\n配置指南: TWITTER_API_CONFIG.md")
    sys.exit(1)

# 测试API连接
print("\n4. 测试Twitter API连接...")
try:
    # 使用API V2 Client (免费层级支持)
    client = tweepy.Client(
        consumer_key=config.TWITTER_API_KEY,
        consumer_secret=config.TWITTER_API_SECRET,
        access_token=config.TWITTER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET
    )
    
    # 验证凭证 - 获取当前认证用户
    print("   验证凭证...")
    me = client.get_me()
    if me.data:
        print(f"✅ API连接成功！")
        print(f"   认证账号: @{me.data.username}")
    else:
        print("⚠️  API连接成功，但无法获取用户信息")
    
except tweepy.errors.Unauthorized:
    print("❌ 认证失败 (401 Unauthorized)")
    print("   请检查密钥是否正确")
    sys.exit(1)
except tweepy.errors.Forbidden as e:
    print(f"❌ 权限不足 (403 Forbidden): {e}")
    print("   API密钥可能需要更高的访问级别")
    # 不退出，继续尝试获取推文
except Exception as e:
    print(f"❌ API连接失败: {e}")
    sys.exit(1)

# 测试获取推文
print(f"\n5. 测试获取 @{config.TRUMP_TWITTER_USERNAME} 的推文...")
try:
    # 先获取用户ID
    user = client.get_user(username=config.TRUMP_TWITTER_USERNAME)
    if not user.data:
        print(f"❌ 用户 @{config.TRUMP_TWITTER_USERNAME} 不存在")
        sys.exit(1)
    
    user_id = user.data.id
    print(f"   用户ID: {user_id}")
    
    # 使用API V2获取推文
    tweets_response = client.get_users_tweets(
        id=user_id,
        max_results=5,
        exclude=['retweets', 'replies'],
        tweet_fields=['created_at', 'text']
    )
    
    if not tweets_response.data:
        print(f"⚠️  用户 @{config.TRUMP_TWITTER_USERNAME} 暂无推文")
        sys.exit(0)
    
    tweets = tweets_response.data
    print(f"✅ 成功获取到 {len(tweets)} 条推文\n")
    
    for i, tweet in enumerate(tweets, 1):
        print(f"推文 {i}:")
        print(f"  ID: {tweet.id}")
        print(f"  时间: {tweet.created_at if hasattr(tweet, 'created_at') else '未知'}")
        print(f"  内容: {tweet.text[:80]}...")
        print(f"  链接: https://twitter.com/{config.TRUMP_TWITTER_USERNAME}/status/{tweet.id}")
        print()
    
except tweepy.errors.NotFound:
    print(f"❌ 用户 @{config.TRUMP_TWITTER_USERNAME} 不存在或已被封禁")
    sys.exit(1)
except tweepy.errors.Forbidden as e:
    print(f"❌ 权限不足 (403 Forbidden)")
    print(f"   错误详情: {e}")
    print("\n可能的原因：")
    print("1. 免费API层级限制，需要升级到Basic或更高级别")
    print("2. 访问 https://developer.x.com/en/portal/products 查看你的访问级别")
    sys.exit(1)
except Exception as e:
    print(f"❌ 获取推文失败: {e}")
    sys.exit(1)

# 测试完成
print("=" * 60)
print("✅ 所有测试通过！")
print("=" * 60)
print("\n现在可以运行: python3 bot.py")
print("机器人将自动监控推特并推送到Telegram群组")
