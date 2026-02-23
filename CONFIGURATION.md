# 📦 配置说明

本项目的所有敏感配置已经脱敏，你需要填写自己的真实密钥才能使用。

## 🚀 快速开始

### 1. 复制配置示例

查看 [CONFIG_EXAMPLE.md](CONFIG_EXAMPLE.md) 了解完整的配置格式。

### 2. 填写真实配置

打开 [config.py](config.py)，将以下占位符替换为真实密钥：

#### ✅ 必填项（核心功能需要）

```python
# Telegram Bot配置
BOT_TOKEN = "YOUR_BOT_TOKEN"  # ← 替换为你的Bot Token
CHAT_ID = "YOUR_CHAT_ID"      # ← 替换为你的群组ID

# Google Gemini AI配置
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # ← 替换为你的Gemini密钥
```

#### ⚠️ 可选项（Twitter监控）

```python
# Twitter API配置（需要Basic层级 $100/月）
TWITTER_API_KEY = "your_api_key_here"
TWITTER_API_SECRET = "your_api_secret_here"
TWITTER_ACCESS_TOKEN = "your_access_token_here"
TWITTER_ACCESS_TOKEN_SECRET = "your_access_token_secret_here"
```

**注意**: 由于Twitter免费API无法监控其他用户，推荐使用RSS Bot替代方案。

### 3. 获取密钥的详细步骤

#### 📱 Telegram Bot Token

1. 在Telegram搜索 `@BotFather`
2. 发送 `/newbot` 创建机器人
3. 按提示设置名称
4. 复制获得的token

#### 🆔 Telegram 群组ID

1. 将机器人添加到群组
2. 在群组发送任意消息
3. 访问: `https://api.telegram.org/bot<你的BOT_TOKEN>/getUpdates`
4. 找到 `"chat":{"id":-1001234567890}`
5. 复制ID（包含负号）

#### 🤖 Google Gemini API

1. 访问: https://makersuite.google.com/app/apikey
2. 点击 "Create API Key"
3. 复制生成的密钥

#### 🐦 Twitter API（可选）

⚠️ **免费层级无法监控其他用户！** 需要Basic层级($100/月)

详见: [TWITTER_FREE_TIER_LIMITS.md](TWITTER_FREE_TIER_LIMITS.md)

推荐免费替代方案：使用Telegram RSS Bot订阅Nitter RSS源

### 4. 验证配置

```bash
# 激活虚拟环境
source .venv/bin/activate

# 快速测试Bot配置
python3 -c "from telegram import Bot; import config; print('✅ Bot:', Bot(config.BOT_TOKEN).get_me().username)"

# 快速测试Gemini配置
python3 -c "import google.generativeai as genai; import config; genai.configure(api_key=config.GEMINI_API_KEY); print('✅ Gemini配置正确')"
```

### 5. 启动机器人

```bash
python3 bot.py
```

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [CONFIG_EXAMPLE.md](CONFIG_EXAMPLE.md) | 完整配置示例（脱敏版） |
| [TWITTER_API_CONFIG.md](TWITTER_API_CONFIG.md) | Twitter API详细配置指南 |
| [TWITTER_FREE_TIER_LIMITS.md](TWITTER_FREE_TIER_LIMITS.md) | Twitter免费API限制说明 |
| [TWITTER_API_SOLUTION.md](TWITTER_API_SOLUTION.md) | Twitter监控替代方案 |

## 🔒 安全提示

1. ✅ `config.py` 已在 `.gitignore` 中，不会被提交
2. ❌ 不要分享你的密钥
3. ❌ 不要截图包含密钥的配置文件
4. ✅ 如果泄露，立即重新生成

## ❓ 常见问题

### Q: 为什么我的config.py显示占位符？

A: 这是脱敏后的示例。你需要手动替换为自己的真实密钥。

### Q: Twitter监控功能可用吗？

A: 免费API不可用。需要：
- Basic层级($100/月) + 填写真实密钥，或
- 使用免费的RSS Bot替代方案（推荐）

### Q: 只想使用价格推送和AI问答，不需要Twitter监控？

A: 完全可以！只需配置：
```python
BOT_TOKEN = "你的token"
CHAT_ID = "你的群组ID"
GEMINI_API_KEY = "你的Gemini密钥"
TRUMP_TWITTER_ENABLED = False  # 禁用Twitter功能
```

### Q: 如何测试配置是否正确？

A: 运行上面的验证命令，或者直接启动bot.py查看日志。

## 💡 提示

- 所有密钥都需要自己申请获取
- 推荐先配置必填项，测试基础功能
- Twitter功能可选，有严格的API限制
- 遇到问题查看相关文档或日志

---

**开始使用**: 按照上述步骤配置后，运行 `python3 bot.py` 即可启动机器人！
