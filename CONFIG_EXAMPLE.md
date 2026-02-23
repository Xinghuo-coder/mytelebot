# 配置文件示例（脱敏版）

## config.py 完整示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
"""

# 电报机器人配置
BOT_TOKEN = "YOUR_BOT_TOKEN"  # 从 @BotFather 获取，格式如: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
CHAT_ID = "YOUR_CHAT_ID"  # 群组ID需要加负号前缀，格式如: -1001234567890

# 定时任务配置
SCHEDULE_TYPE = "daily"
SCHEDULE_HOURS = [7, 12, 15, 17, 21]
SCHEDULE_MINUTES = {7: 30, 17: 50}

# API配置
REQUEST_TIMEOUT = 10

# AI配置（Google Gemini）
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # 从 https://makersuite.google.com/app/apikey 获取
GEMINI_MODEL = "gemini-2.5-flash"
AI_MAX_TOKENS = 500
AI_TEMPERATURE = 0.7
AI_ENABLED = True

# X/Twitter推特监控配置
TRUMP_TWITTER_ENABLED = False  # 免费API无法使用，建议使用RSS Bot替代
TRUMP_TWITTER_USERNAME = "elonmusk"
TRUMP_CHECK_INTERVAL = 3

# Twitter API官方密钥（从 https://developer.twitter.com/ 获取）
# ⚠️ 注意：免费层级API无法监控其他用户，需要Basic层级($100/月)才能使用
# 推荐使用Telegram RSS Bot作为免费替代方案，详见 TWITTER_FREE_TIER_LIMITS.md
TWITTER_API_KEY = "your_api_key_here"  # API Key - 约25字符
TWITTER_API_SECRET = "your_api_secret_here"  # API Secret - 约50字符
TWITTER_ACCESS_TOKEN = "your_access_token_here"  # Access Token - 格式: 数字-字母
TWITTER_ACCESS_TOKEN_SECRET = "your_access_token_secret_here"  # Token Secret - 约45字符
TWITTER_USE_OFFICIAL_API = True  # 使用官方API（需要Basic层级或更高）

# 备用方案：Nitter实例（当官方API不可用时）
TRUMP_NITTER_INSTANCES = [
    "https://nitter.cz",
    "https://nitter.privacytools.io",
]
```

## 如何填写真实配置

### 1. Telegram Bot 配置

**获取 BOT_TOKEN:**
1. 在Telegram搜索 `@BotFather`
2. 发送 `/newbot` 创建机器人
3. 复制得到的token，格式如: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

**获取 CHAT_ID:**
1. 将机器人添加到群组
2. 在群组发送一条消息
3. 访问: `https://api.telegram.org/bot<你的BOT_TOKEN>/getUpdates`
4. 找到 `"chat":{"id":-1001234567890}` 中的ID
5. 群组ID带负号

### 2. Google Gemini API

1. 访问: https://makersuite.google.com/app/apikey
2. 点击 "Create API Key"
3. 复制密钥，格式如: `AIzaSyAbCdEf...`

### 3. Twitter API（可选）

⚠️ **重要**: 免费层级无法监控其他用户的推特！

如果你有Basic层级($100/月)或更高：

1. 访问: https://developer.twitter.com/
2. 进入你的App → Keys and tokens
3. 复制4个密钥：
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)  
   - Access Token
   - Access Token Secret

**密钥格式示例**（这些是示例，不是真实密钥）：
```
API Key: xvz1evFS4wEEPTGEFPHBog
API Secret: L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg
Access Token: 1234567890-AbcdEfghIjklMnopQrstUvwxYz
Access Token Secret: AbcDefGhIjKlMnOpQrStUvWxYz1234567890
```

## 安全提示

1. ❌ **不要将真实配置提交到Git**
2. ❌ **不要分享你的密钥**
3. ✅ 将 `config.py` 添加到 `.gitignore`
4. ✅ 如果泄露，立即重新生成密钥

## 示例 .gitignore

```gitignore
# 配置文件（包含密钥）
config.py

# Python缓存
__pycache__/
*.pyc
*.pyo

# 虚拟环境
.venv/
venv/

# 数据文件
sent_tweets.json
*.log
```

## 验证配置

填写完成后，运行测试：

```bash
# 测试Telegram Bot
.venv/bin/python3 -c "from telegram import Bot; import config; bot = Bot(config.BOT_TOKEN); print('✅ Bot配置正确:', bot.get_me().username)"

# 测试Gemini API
.venv/bin/python3 -c "import google.generativeai as genai; import config; genai.configure(api_key=config.GEMINI_API_KEY); print('✅ Gemini配置正确')"

# 测试Twitter API（如果配置了）
.venv/bin/python3 test_twitter_api.py
```

## Twitter监控替代方案

由于免费Twitter API限制严格，推荐使用：

### Telegram RSS Bot（免费）

1. 搜索 `@RSSTBot` 或 `@TheFeedReaderBot`
2. 发送命令：
   ```
   /sub https://nitter.net/elonmusk/rss
   ```
3. 将Bot添加到群组

详见: [TWITTER_FREE_TIER_LIMITS.md](TWITTER_FREE_TIER_LIMITS.md)
