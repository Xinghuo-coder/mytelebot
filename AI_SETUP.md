# 机器人AI功能设置指南

## 功能说明

机器人现在已集成Google Gemini AI问答功能，可以：
1. 继续定时推送金融市场价格信息
2. 回答群组中@机器人或回复机器人消息时提出的问题

## 配置步骤

### 1. 获取Google Gemini API密钥

您已经有一个配置好的API密钥！当前配置：
- API密钥: `AIzaSyDf7pui4S6F4es6eep5--9nd7C6-wYwI0I`
- 模型: `gemini-2.0-flash-exp`

如需获取新的API密钥：
1. 访问 https://makersuite.google.com/app/apikey
2. 登录Google账号
3. 点击"Create API key"创建API密钥
4. 复制生成的密钥

### 2. 配置API密钥

编辑 `config.py` 文件，当前配置如下：

```python
GEMINI_API_KEY = "AIzaSyDf7pui4S6F4es6eep5--9nd7C6-wYwI0I"
GEMINI_MODEL = "gemini-2.0-flash-exp"
AI_ENABLED = True
```

### 3. 配置选项说明

在 `config.py` 中可以调整以下AI参数：

```python
GEMINI_MODEL = "gemini-2.0-flash-exp"  # AI模型选择
# 可选模型:
# - "gemini-2.0-flash-exp" (推荐，最新实验版本)
# - "gemini-1.5-flash" (快速，成本低)
# - "gemini-1.5-pro" (高性能)
# - "gemini-pro" (标准版)

AI_MAX_TOKENS = 500  # 回复的最大长度（token数）
AI_TEMPERATURE = 0.7  # 创造性程度（0-1，越高越有创意）
AI_ENABLED = True  # 是否启用AI功能
```

## 使用方法

### 群组中使用

1. **@机器人提问**
   ```
   @你的机器人 比特币是什么？
   ```

2. **回复机器人的消息**
   - 点击回复机器人发送的任何消息
   - 输入你的问题

### 机器人命令

- `/start` - 查看机器人介绍
- `/help` - 查看使用说明

## 启动机器人

```bash
cd /Users/macbookpro/telebot
source .venv/bin/activate
python bot.py
```

## 注意事项

1. **免费额度**: Google Gemini API提供免费额度，具有一定的速率限制
2. **隐私保护**: 请妥善保管API密钥，不要泄露或提交到公开代码库
3. **速率限制**: Gemini有API调用速率限制，具体限制取决于您的配额
4. **关闭AI功能**: 如需关闭AI功能，将 `AI_ENABLED` 设为 `False`

## 故障排查

### 机器人不回复问题
- 检查是否@了机器人或回复了机器人的消息
- 检查 `AI_ENABLED` 是否为 `True`
- 检查API密钥是否正确配置
- 查看日志输出是否有错误信息

### API错误
- 检查API密钥是否有效
- 检查是否超过了速率限制
- 检查网络连接

## 测试AI功能

运行测试脚本来验证AI功能：

```bash
cd /Users/macbookpro/telebot
source .venv/bin/activate
python test_ai.py
```

这将运行几个测试问题并显示AI的回答。

## 高级配置

### 切换到OpenAI

如果想使用OpenAI而不是Gemini，需要：
1. 修改 `requirements.txt`，将 `google-generativeai` 替换为 `openai`
2. 修改 `bot.py` 中的AI调用代码
3. 在 `config.py` 中配置OpenAI API密钥

### 自定义AI提示词

在 `bot.py` 的 `ask_ai()` 函数中，你可以添加系统提示：

```python
prompt = f"你是一个友好、专业的金融顾问。用户问题：{question}"
response = await asyncio.to_thread(gemini_model.generate_content, prompt, ...)
```

## 更新日志

- 2026-02-03: 添加Google Gemini AI问答功能，支持@机器人和回复消息提问
