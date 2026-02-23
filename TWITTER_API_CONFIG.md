# Twitter API 配置指南

## 📋 需要的密钥

在 https://developer.twitter.com/ 注册后，你需要获取以下**4个密钥**：

### 1. API Key (Consumer Key)
```
格式示例: xvz1evFS4wEEPTGEFPHBog
```

### 2. API Secret (Consumer Secret)
```
格式示例: L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg
```

### 3. Access Token
```
格式示例: 1234567890-AbcdEfghIjklMnopQrstUvwxYz123456789
```

### 4. Access Token Secret
```
格式示例: AbcDefGhIjKlMnOpQrStUvWxYz1234567890AbCdEf
```

## 🔧 配置步骤

### 步骤1: 安装 tweepy 库

在终端运行：
```bash
cd /Users/macbookpro/telebot
source .venv/bin/activate
pip install tweepy
```

### 步骤2: 填写密钥到 config.py

打开 [config.py](config.py)，找到这几行并替换为你的密钥：

```python
# Twitter API官方密钥（从 https://developer.twitter.com/ 获取）
TWITTER_API_KEY = "你的API_Key"  # 替换这里
TWITTER_API_SECRET = "你的API_Secret"  # 替换这里
TWITTER_ACCESS_TOKEN = "你的Access_Token"  # 替换这里
TWITTER_ACCESS_TOKEN_SECRET = "你的Access_Token_Secret"  # 替换这里
TWITTER_USE_OFFICIAL_API = True  # 保持True
```

### 步骤3: 设置监控的用户名

```python
TRUMP_TWITTER_USERNAME = "elonmusk"  # 改为你想监控的用户名
TRUMP_TWITTER_ENABLED = True  # 确保为True
```

### 步骤4: 运行测试

```bash
.venv/bin/python3 -c "
import tweepy
import config

auth = tweepy.OAuthHandler(config.TWITTER_API_KEY, config.TWITTER_API_SECRET)
auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# 测试获取推文
tweets = api.user_timeline(screen_name=config.TRUMP_TWITTER_USERNAME, count=1)
for tweet in tweets:
    print(f'✅ 成功！获取到推文: {tweet.text[:50]}...')
"
```

如果看到 `✅ 成功！` 说明配置正确。

### 步骤5: 启动机器人

```bash
.venv/bin/python3 bot.py
```

## 🎯 获取密钥的详细步骤

### 在 Twitter Developer Portal

1. **登录**: https://developer.twitter.com/
2. **创建项目**: Projects & Apps → Create App
3. **生成密钥**: 在 Keys and tokens 标签页

#### 获取 API Key 和 API Secret
- 点击 "Consumer Keys" 下的 "Regenerate" 按钮
- 会显示 API Key 和 API Secret
- **立即复制保存**（关闭后无法再查看）

#### 获取 Access Token 和 Access Token Secret
- 点击 "Authentication Tokens" 下的 "Generate" 按钮
- 会显示 Access Token 和 Access Token Secret  
- **立即复制保存**（关闭后无法再查看）

## 📝 示例配置

```python
# 完整示例（请替换为你的真实密钥）
TWITTER_API_KEY = "your_api_key_here"  # 从Twitter Developer Portal复制
TWITTER_API_SECRET = "your_api_secret_here"  # 从Twitter Developer Portal复制
TWITTER_ACCESS_TOKEN = "your_access_token_here"  # 从Twitter Developer Portal生成
TWITTER_ACCESS_TOKEN_SECRET = "your_access_token_secret_here"  # 从Twitter Developer Portal生成
TWITTER_USE_OFFICIAL_API = True

# 监控马斯克的推特（需要Basic层级API，$100/月）
TRUMP_TWITTER_USERNAME = "elonmusk"
TRUMP_TWITTER_ENABLED = False  # 免费API无法使用，建议改用RSS Bot
TRUMP_CHECK_INTERVAL = 3  # 每3分钟检查一次
```

⚠️ **重要提示**: Twitter免费API无法监控其他用户的推特！需要升级到Basic层级($100/月)。推荐使用免费的Telegram RSS Bot替代方案。

## ⚠️ 注意事项

### 1. 保密密钥
- ❌ 不要将密钥提交到Git
- ❌ 不要分享密钥给他人
- ✅ 如果泄露，立即在Twitter Developer Portal重新生成

### 2. API限制
Twitter API有速率限制：
- **免费账号**: 每15分钟可获取900条推文
- **建议间隔**: 3-5分钟检查一次
- **监控账号**: 建议不超过10个

### 3. App权限
确保你的App有 "Read" 权限（默认即可）

## 🔍 常见问题

### Q1: tweepy安装失败？
```bash
# 尝试升级pip
pip install --upgrade pip
# 再次安装
pip install tweepy
```

### Q2: 401 Unauthorized 错误？
- 检查密钥是否正确复制
- 确认没有多余的空格或引号
- 尝试重新生成密钥

### Q3: 403 Forbidden 错误？
- 检查App权限设置
- 确认Twitter账号状态正常

### Q4: 监控的账号被封禁？
- `realDonaldTrump` 已被永久封禁
- 改为监控其他活跃账号

### Q5: 想监控多个账号？
可以添加多个监控任务，修改 bot.py：
```python
MONITOR_USERS = ["elonmusk", "BarackObama", "BillGates"]
# 循环监控每个用户
```

## ✅ 验证配置

运行完整测试：
```bash
cd /Users/macbookpro/telebot
source .venv/bin/activate
python3 bot.py
```

看到以下日志表示成功：
```
川普推特监控已启用，每3分钟检查一次
立即检查川普推特...
开始检查川普推特...
从Twitter官方API获取到 X 条推文
✅ 成功发送推文 @elonmusk ID: XXXXX
```

## 📞 获取帮助

如果遇到问题：
1. 检查密钥是否正确
2. 确认tweepy已安装
3. 查看错误日志详细信息
4. 参考Twitter API文档: https://developer.twitter.com/en/docs

---

**配置完成后，机器人将自动监控指定Twitter账号并实时推送到Telegram群组！** 🎉
