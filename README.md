# 📱 电报机器人 - 金融价格定时推送 + AI问答

自动定时发送金融市场价格到电报群组，并支持AI智能问答。

## 📑 目录

- [功能特点](#功能特点)
- [快速开始](#快速开始)
- [详细安装步骤](#详细安装步骤)
- [配置说明](#配置说明)
- [AI功能使用](#ai功能使用)
- [定时任务配置](#定时任务配置)
- [后台运行](#后台运行)
- [价格数据来源](#价格数据来源)
- [故障排查](#故障排查)
- [Twitter监控功能](#twitter监控功能)
- [更新日志](#更新日志)

## ✨ 功能特点

### 核心功能
- 📊 **实时获取金融市场价格** - 自动获取多种金融资产价格
- 📈 **显示24小时涨跌幅** - 直观展示市场变化百分比
- ⏰ **定时自动推送** - 每天7次定时推送，不错过重要时刻
- 🤖 **AI智能问答** - 基于Google Gemini 2.5的智能对话功能
- 🗣️ **多种提问方式** - 支持@机器人或回复消息提问

### 支持的资产价格
- 🪙 **BTC** - 比特币
- 💎 **ETH** - 以太坊
- 💰 **伦敦金现货** - 美元/盎司
- 🏆 **上海金现货** - 人民币/克
- 💵 **美元指数** - DXY
- 💴 **美元/人民币** - USD/CNY汇率
- 🛢️ **WTI原油** - 西德克萨斯中质原油
- 📊 **上证指数** - 000001.SS
- 📊 **纳斯达克指数** - ^IXIC
- 📊 **道琼斯指数** - ^DJI
- 📊 **恒生指数** - ^HSI
- 🔬 **恒生科技指数** - HSTECH.HK

## 🚀 快速开始

### 前置要求
- Python 3.7 或更高版本
- Telegram账号
- Google Gemini API密钥（用于AI功能）

### 一键安装运行

```bash
# 1. 克隆或下载项目
cd /Users/macbookpro/telebot

# 2. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置
cp config.example.py config.py
# 编辑 config.py 填入您的配置信息

# 5. 运行
python bot.py
```

## 📦 详细安装步骤

### 1. 配置 Python 环境

本项目使用虚拟环境 `.venv`，确保依赖隔离：

```bash
# macOS/Linux - 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# Windows
# .venv\Scripts\activate
```

### 2. 安装依赖包

```bash
# 激活虚拟环境后
pip install -r requirements.txt

# 或者直接使用虚拟环境的 pip（无需激活）
.venv/bin/pip install -r requirements.txt
```

### 3. 配置文件设置

**重要：首次使用需要配置敏感信息**

```bash
# 复制配置模板
cp config.example.py config.py

# 编辑 config.py 填入您的配置信息
```

## ⚙️ 配置说明

### 必填配置项

编辑 `config.py` 文件，填写以下必需配置：

```python
# Telegram Bot 配置
BOT_TOKEN = "YOUR_BOT_TOKEN"  # 从 @BotFather 获取
CHAT_ID = "YOUR_CHAT_ID"      # 群组ID（带负号前缀）

# Google Gemini AI 配置
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # 从 Google AI Studio 获取
GEMINI_MODEL = "gemini-2.5-flash"       # AI模型（推荐）
AI_ENABLED = True                       # 是否启用AI功能
```

### 获取配置密钥

#### 1. Telegram Bot Token

1. 在Telegram搜索 `@BotFather`
2. 发送 `/newbot` 创建机器人
3. 按提示设置名称
4. 复制获得的token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

#### 2. Telegram 群组ID

1. 将机器人添加到群组
2. 在群组发送任意消息
3. 访问：`https://api.telegram.org/bot<你的BOT_TOKEN>/getUpdates`
4. 找到 `"chat":{"id":-1001234567890}`
5. 复制ID（**必须包含负号**）

#### 3. Google Gemini API密钥

1. 访问：https://aistudio.google.com/app/apikey
2. 登录Google账号
3. 点击 "Create API Key"
4. 复制生成的密钥

#### 4. 关闭机器人隐私模式（重要！）

**必须执行此步骤，否则机器人无法接收群组消息：**

1. 在Telegram找 @BotFather
2. 发送：`/setprivacy`
3. 选择你的机器人
4. 选择：**Disable**

### 可选配置

```python
# AI参数调整
AI_MAX_TOKENS = 500      # 回复的最大长度
AI_TEMPERATURE = 0.7     # 创造性程度（0-1，越高越有创意）

# 定时任务配置
SCHEDULE_TYPE = "daily"
SCHEDULE_HOURS = [7, 11, 15, 17, 20, 21, 22]  # 推送时间点
SCHEDULE_MINUTES = {7: 30, 17: 40}            # 特定时间的分钟数

# Twitter监控（可选）
TRUMP_TWITTER_ENABLED = False     # 是否启用Twitter监控
TRUMP_TWITTER_USERNAME = "elonmusk"  # 监控的用户名
TRUMP_CHECK_INTERVAL = 3          # 检查间隔（分钟）
```

### 可用的AI模型

推荐使用以下稳定模型：
- `gemini-2.5-flash` - ⭐推荐，快速且稳定
- `gemini-2.5-pro` - 高质量，功能更强
- `gemini-2.0-flash` - 也很稳定

### 验证配置

```bash
# 测试Telegram Bot配置
python3 -c "from telegram import Bot; import config; print('✅ Bot:', Bot(config.BOT_TOKEN).get_me().username)"

# 测试Gemini API配置
python3 -c "import google.generativeai as genai; import config; genai.configure(api_key=config.GEMINI_API_KEY); print('✅ Gemini配置正确')"
```

## 🤖 AI功能使用

### 在群组中使用AI问答

机器人启动后，有两种方式使用AI问答功能：

#### 方式1: @机器人提问
```
@你的机器人用户名 比特币是什么？
@你的机器人用户名 如何理财？
```

#### 方式2: 回复机器人的消息
- 点击回复机器人发送的任何消息
- 输入你的问题

### 机器人命令

- `/start` - 查看机器人介绍
- `/help` - 查看使用说明

机器人会显示"🤔 正在思考..."的提示，然后用AI回复你的问题。

### AI功能特点

- 🧠 使用Google Gemini 2.5 Flash模型
- 🇨🇳 中文回答，简洁清晰
- ⚡ 快速响应
- 💬 上下文理解
- 🎯 专业金融知识

## ⏰ 定时任务配置

### 默认推送时间

每天7个时间点执行价格推送：
- 🌅 早上 07:30
- ☀️ 上午 11:30
- 🌤️ 下午 15:00
- 🌆 下午 17:40
- 🌙 晚上 20:00
- 🌙 晚上 21:00
- 🌙 晚上 22:00

财经日历推送（每天2次）：
- 🌅 早上 07:00
- 🌙 晚上 21:00

### 自定义定时规则

可以在 `bot.py` 中修改定时规则：

#### 每小时执行
```python
scheduler.add_job(
    send_price_update,
    CronTrigger(minute=0),  # 每小时整点
)
```

#### 每天特定时间执行
```python
scheduler.add_job(
    send_price_update,
    CronTrigger(hour='9,12,15,18', minute=0),  # 9:00, 12:00, 15:00, 18:00
)
```

#### 每隔N分钟执行
```python
scheduler.add_job(
    send_price_update,
    'interval',
    minutes=30,  # 每30分钟
)
```

## 🖥️ 后台运行

### macOS/Linux

#### 方式1: 使用 nohup
```bash
nohup python bot.py > bot.log 2>&1 &
```

#### 方式2: 使用 screen
```bash
screen -S telebot
python bot.py
# 按 Ctrl+A, 然后按 D 来分离
```

#### 方式3: 使用 systemd（Linux）

创建服务文件：
```bash
sudo nano /etc/systemd/system/telebot.service
```

内容：
```ini
[Unit]
Description=Telegram Price Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/Users/macbookpro/telebot
ExecStart=/Users/macbookpro/telebot/.venv/bin/python /Users/macbookpro/telebot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start telebot
sudo systemctl enable telebot  # 开机自启
sudo systemctl status telebot  # 查看状态
```

#### 方式4: 使用 launchd（macOS）

创建plist文件：
```bash
nano ~/Library/LaunchAgents/com.telebot.plist
```

内容：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.telebot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/macbookpro/telebot/.venv/bin/python</string>
        <string>/Users/macbookpro/telebot/bot.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/macbookpro/telebot</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/macbookpro/telebot/bot.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/macbookpro/telebot/bot_error.log</string>
</dict>
</plist>
```

加载服务：
```bash
launchctl load ~/Library/LaunchAgents/com.telebot.plist
launchctl start com.telebot
```

查看状态：
```bash
launchctl list | grep telebot
```

停止服务：
```bash
launchctl stop com.telebot
launchctl unload ~/Library/LaunchAgents/com.telebot.plist
```

## 📊 价格数据来源

所有价格数据均来自可靠的API，包含24小时涨跌幅：

| 资产 | 数据来源 | 说明 |
|------|---------|------|
| 伦敦金 | fx168news.com | 伦敦金现货行情，美元/盎司 |
| 上海金 | 换算 | 基于伦敦金价格和USD/CNY汇率实时换算 |
| 美元指数 | Yahoo Finance | DX-Y.NYB |
| USD/CNY | Yahoo Finance | CNY=X |
| WTI原油 | Yahoo Finance | CL=F期货 |
| BTC | Yahoo Finance | BTC-USD |
| ETH | Yahoo Finance | ETH-USD |
| 上证指数 | Yahoo Finance | 000001.SS |
| 纳斯达克 | Yahoo Finance | ^IXIC |
| 道琼斯 | Yahoo Finance | ^DJI |
| 恒生指数 | Yahoo Finance | ^HSI |
| 恒生科技 | Yahoo Finance | HSTECH.HK |

### 价格显示说明

每个资产价格都会显示：
- ✅ 当前价格
- 📈 上涨或 📉 下跌符号
- ✅ 24小时涨跌幅百分比（如 +2.35% 或 -1.20%）

**伦敦金特殊说明**：
- 使用fx168news.com伦敦金现货行情
- 单位：美元/盎司
- 24小时实时更新价格和涨跌幅
- 自动检测周末和闭市状态
- 周末或闭市时标注状态 `[周五收盘]` 或 `[收盘]`

**上海金特殊说明**：
- 价格基于伦敦金现货价格和USD/CNY汇率实时换算得出
- 单位：人民币/克（¥/克）
- 计算公式：伦敦金价格(美元/盎司) × USD/CNY汇率 ÷ 31.1035克/盎司
- 涨跌幅直接使用伦敦金的24小时涨跌幅（因为价格基于伦敦金换算）
- 价格与上海黄金交易所现货金价格高度相关

## 🔧 故障排查

### 1. 消息发送失败

**可能原因：**
- 机器人不在群组中
- 群组ID不正确
- 机器人没有发送消息权限

**解决方案：**
- 检查机器人是否在群组中
- 确认群组ID是否正确（需要负号前缀）
- 检查机器人在群组的权限设置

### 2. 价格获取失败

**可能原因：**
- 网络连接问题
- API临时不可用

**解决方案：**
- 检查网络连接
- 程序会自动重试
- 查看日志了解具体错误

### 3. AI不回复问题 ⭐重要

**必须首先确认：已关闭隐私模式！**

步骤：
1. 在Telegram找 @BotFather
2. 发送：`/setprivacy`
3. 选择你的机器人
4. 选择：**Disable**

**其他检查项：**
- [ ] 是否@了机器人或回复了机器人的消息
- [ ] `config.py` 中 `AI_ENABLED` 是否为 `True`
- [ ] Google Gemini API密钥是否正确配置
- [ ] 是否超过了API速率限制

**如果提示模型错误：**
```bash
# 运行测试查看可用模型
python test_gemini.py
```

### 4. 查看日志

程序会输出详细日志信息：

```bash
# 查看主要日志（推荐）
tail -f /Users/macbookpro/telebot/bot_error.log

# 查看辅助日志
tail -f /Users/macbookpro/telebot/bot.log

# 查看定时任务执行记录
grep "消息发送成功" /Users/macbookpro/telebot/bot_error.log
```

### 5. 常用调试命令

```bash
# 检查机器人进程
ps aux | grep bot.py

# 检查服务状态（launchd）
launchctl list | grep telebot

# 检查服务状态（systemd）
sudo systemctl status telebot

# 重启机器人
./restart_bot.sh
```

## 🐦 Twitter监控功能

### ⚠️ 重要说明

Twitter监控功能目前**受限**：
- ❌ Twitter免费API不支持监控其他用户
- ✅ 需要Basic层级（$100/月）或更高
- ✅ 推荐使用免费替代方案

### 免费替代方案：RSS订阅

使用Telegram RSS Bot订阅Twitter RSS源：

#### 步骤：

1. **在Telegram搜索并启动**：`@RSSTBot` 或 `@TheFeedReaderBot`

2. **订阅Twitter用户**：
   ```
   /sub https://nitter.net/elonmusk/rss
   /sub https://nitter.cz/realDonaldTrump/rss
   ```

3. **配置推送**：
   - 将RSS Bot添加到你的群组
   - Bot会自动推送新推文

#### 可用的Nitter RSS源：
```
https://nitter.net/[用户名]/rss
https://nitter.cz/[用户名]/rss
https://nitter.privacytools.io/[用户名]/rss
```

### 使用Twitter官方API（付费）

如果你有Twitter API密钥（Basic层级或更高）：

#### 1. 安装tweepy
```bash
pip install tweepy
```

#### 2. 配置API密钥

编辑 `config.py`：
```python
# Twitter API配置
TWITTER_API_KEY = "你的API_Key"
TWITTER_API_SECRET = "你的API_Secret"
TWITTER_ACCESS_TOKEN = "你的Access_Token"
TWITTER_ACCESS_TOKEN_SECRET = "你的Access_Token_Secret"
TWITTER_USE_OFFICIAL_API = True

# 监控设置
TRUMP_TWITTER_ENABLED = True
TRUMP_TWITTER_USERNAME = "elonmusk"
TRUMP_CHECK_INTERVAL = 3  # 每3分钟检查一次
```

#### 3. 获取Twitter API密钥

1. 访问：https://developer.twitter.com/
2. 创建开发者账号
3. 创建App并获取以下密钥：
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret

#### 4. 测试配置

```bash
python test_twitter_api.py
```

### 工作原理

```
定时任务(每3分钟)
    ↓
检查Twitter账号
    ↓
过滤新推文(去重)
    ↓
发送到Telegram群组
    ↓
保存推文ID(避免重复)
```

### 消息格式

当检测到新推文时，机器人会发送：

```
🐦 [用户名] 推特更新

[推文内容]

🔗 查看原推文
🕐 [发布时间]
```

### 注意事项

1. ⚠️ Twitter免费API限制严格，推荐使用RSS方案
2. 💰 官方API需要付费（Basic层级$100/月）
3. 📊 监控频率建议：3-5分钟
4. 🔐 保护好API密钥，不要泄露
5. 📝 `sent_tweets.json` 文件用于存储已发送的推文ID

## 📝 更新日志

### v1.3 - 2026-02-26
- ✨ 新增恒生科技指数监控
- 📊 优化定时任务配置
- 🐛 修复多处文档错误

### v1.2 - 2026-02-03
- ✨ AI功能集成完成
- 🤖 添加Google Gemini支持
- 📚 完善文档和故障排查指南
- 🐛 修复AI模型404错误
- 🐛 修复机器人隐私模式问题

### v1.1 - 2026-02-23
- ✨ 添加Twitter监控功能
- 📊 新增多个股指支持
- 🔧 改进定时任务机制

### v1.0 - 初始版本
- 📊 基础价格推送功能
- ⏰ 定时任务支持
- 📈 多种资产价格监控

## 🔒 注意事项

1. ✅ 确保机器人已被添加到群组并有发送消息权限
2. ✅ 群组ID需要添加负号前缀（如 `-5239428550`）
3. ✅ API调用有频率限制，建议不要设置过于频繁的更新
4. ✅ 建议使用虚拟环境运行，避免依赖冲突
5. ✅ **机器人需关闭隐私模式才能接收群组消息**：找 @BotFather → `/setprivacy` → Disable
6. ✅ Google Gemini API免费额度充足，具体限制请查看Google AI Studio
7. ✅ 妥善保管API密钥，不要泄露或提交到公开代码库
8. ✅ `config.py` 已在 `.gitignore` 中，不会被提交到Git

## 🛠️ 技术栈

- **编程语言**: Python 3.7+
- **电报机器人**: python-telegram-bot 20.7
- **AI服务**: Google Gemini API
- **AI模型**: gemini-2.5-flash
- **调度器**: APScheduler
- **异步HTTP**: aiohttp
- **数据解析**: BeautifulSoup4, lxml

## 📚 项目文件说明

| 文件 | 说明 |
|------|------|
| bot.py | 主程序文件 |
| config.py | 配置文件（需要自己创建） |
| config.example.py | 配置文件模板 |
| requirements.txt | Python依赖包列表 |
| test_*.py | 各种测试脚本 |
| sent_tweets.json | 已发送推文记录 |
| bot.log | 辅助日志文件 |
| bot_error.log | 主要日志文件 |
| start_bot.sh | 启动脚本 |
| restart_bot.sh | 重启脚本 |

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如果遇到问题：
1. 查看本文档的[故障排查](#故障排查)部分
2. 查看日志文件获取详细错误信息
3. 运行测试脚本验证配置
4. 提交Issue描述问题

---

**祝使用愉快！** 🎉
