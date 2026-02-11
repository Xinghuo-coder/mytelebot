# 电报机器人 - 金融价格定时推送 + AI问答

自动定时发送金融市场价格到电报群组，并支持AI智能问答。

## 功能特点

- 📊 实时获取金融市场价格
- 📈 显示24小时涨跌幅百分比
- ⏰ 定时自动推送（每天7次）
- 🤖 AI智能问答功能
- 🗣️ 支持@机器人或回复消息提问
- 📈 支持多种资产价格：
  - 🪙 BTC（比特币）
  - 💎 ETH（以太坊）
  - 💰 伦敦金现货（美元/盎司）
  - 🏆 上海金现货（人民币/克）
  - 💵 美元指数
  - 💴 美元/人民币汇率
  - 🛢️ WTI 原油
  - 📊 上证指数

## 安装步骤

### 1. 配置 Python 环境（推荐）

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

### 3. 配置信息

**重要：首次使用需要配置敏感信息**

复制配置模板文件并填入您的真实配置：

```bash
# 复制配置模板
cp config.example.py config.py

# 编辑 config.py 填入您的配置信息
# - BOT_TOKEN: 从 @BotFather 获取
# - CHAT_ID: 您的群组ID
# - GEMINI_API_KEY: 从 https://aistudio.google.com/app/apikey 获取
```

配置项说明：
- `BOT_TOKEN`: Telegram Bot Token（从 @BotFather 获取）
- `CHAT_ID`: 群组ID（需要加负号前缀）
- `GEMINI_API_KEY`: Google Gemini API密钥（可选，用于AI功能）
- `GEMINI_MODEL`: AI模型（推荐: gemini-2.5-flash）
- `AI_ENABLED`: 是否启用AI功能（True/False）

详细的AI功能配置和使用说明，请查看 [AI_SETUP.md](AI_SETUP.md) 文件。

## 运行

### 方式一：激活虚拟环境后运行（推荐）
```bash
source .venv/bin/activate  # 激活虚拟环境
python bot.py              # 运行机器人
```

### 方式二：直接使用虚拟环境 Python
```bash
.venv/bin/python bot.py
```

### macOS 注意事项
macOS 系统上 Python 3 命令为 `python3`，如果未使用虚拟环境：
```bash
python3 bot.py
```

## AI问答使用方法

机器人启动后，在群组中有两种方式使用AI问答功能：

### 1. @机器人提问
```
@你的机器人 比特币是什么？
@你的机器人 如何理财？
```

### 2. 回复机器人的消息
- 点击回复机器人发送的任何消息
- 输入你的问题

### 机器人命令
- `/start` - 查看机器人介绍
- `/help` - 查看使用说明

机器人会显示"🤔 正在思考..."的提示，然后用AI回复你的问题。

## 定时任务配置
天7个时间点**执行：
- 🌅 早上 7:30
- ☀️ 上午 11:30
- 🌤️ 下午 15:00
- 🌆 下午 17:40
- 🌙 晚上 20:00
- 🌙 晚上 21:00
- 🌙 晚上 22:00

可以在 `bot.py` 中修改定时规则。

### 其他定时选项

每小时执行：
```python
scheduler.add_job(
    send_price_update,
    CronTrigger(minute=0),  # 每小时整点
)
```

每天特定时间执行：
```python
scheduler.add_job(
    send_price_update,
    CronTrigger(hour='9,12,15,18', minute=0),  # 每天9:00, 12:00, 15:00, 18:00
)
```

每隔N分钟执行：
```python
scheduler.add_job(
    send_price_update,
    'interval',
    minutes=30,  # 每30分钟
)
```
source .venv/bin/activate

## 后台运行

### macOS/Linux

使用 `nohup`：
```bash
nohup python bot.py > bot.log 2>&1 &
```

使用 `screen`：
```bashLinux）

创建 systemd 服务文件：
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

### macOS - 使用 launchd

创建 plist 文件：
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

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start telebot
sudo systemctl enable telebot  # 开机自启
sudo systemctl status telebot  # 查看状态
```

所有价格数据均来自可靠的API,包含24小时涨跌幅：
- **伦敦金**: fx168news.com (伦敦金现货行情)
- **上海金**: 基于伦敦金现货价格和USD/CNY汇率实时换算（价格 = 伦敦金(美元/盎司) × 汇率 ÷ 31.1035，涨跌幅同伦敦金）
- **美元指数**: Yahoo Finance (DX-Y.NYB)
- **美元/人民币**: Yahoo Finance (CNY=X)
- **原油**: Yahoo Finance (WTI期货 CL=F)
- **BTC**: Yahoo Finance (BTC-USD)
- **ETH**: Yahoo Finance (ETH-USD)

## 价格显示说明

每个资产价格都会显示：
- 当前价格
- 📈 上涨或 📉 下跌符号
- 24小时涨跌幅百分比（如 +2.35% 或 -1.20%）

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

## 注意事项

1. 确保机器人已被添加到群组并有发送消息权限
2. 群组ID需要添加负号前缀（如 `-5239428550`）
3. API调用有频率限制，建议不要设置过于频繁的更新
4. 建议使用虚拟环境运行，避免依赖冲突
5. **AI功能需要配置Google Gemini API密钥，详见 [AI_SETUP.md](AI_SETUP.md)**
6. **机器人需关闭隐私模式才能接收群组消息**：找 @BotFather → `/setprivacy` → Disable
7. Google Gemini API免费额度充足，具体限制请查看Google AI Studio

## 故障排查

1. **消息发送失败**
   - 检查机器人是否在群组中
   - 检查群组ID是否正确（需要负号前缀）
   - 检查机器人是否有发送消息权限

2. **价格获取失败**
   - 检查网络连接
   - API可能临时不可用，会自动重试

3. **AI不回复问题**
   - **首先确认已关闭隐私模式**：找 @BotFather → `/setprivacy` → 选择机器人 → Disable
   - 或者将机器人设置为群组管理员
   - 检查是否@了机器人或回复了机器人的消息
   - 检查 `config.py` 中 `AI_ENABLED` 是否为 `True`
   - 检查Google Gemini API密钥是否正确配置
   - 如果提示模型错误，运行 `python test_gemini.py` 查看可用模型
   - 检查是否超过了API速率限制

4. **查看日志**
   - 程序会输出详细日志信息
   - 如使用后台运行，检查 `bot_error.log` 文件（主要日志）和 `bot.log` 文件
   - 运行 `./check_logs.sh` 可实时查看日志
   - 或使用 `tail -f /Users/macbookpro/telebot/bot_error.log`

## 许可证

MIT License
