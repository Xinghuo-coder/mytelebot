# 🤖 机器人AI功能快速开始

## ✅ 已完成配置

您的电报机器人已经成功集成了Google Gemini AI功能！

## 🚀 启动机器人

```bash
cd /Users/macbookpro/telebot
source .venv/bin/activate
python bot.py
```

## 💬 使用AI问答

### 方式1: @机器人
在群组中发送消息：
```
@你的机器人用户名 比特币现在适合投资吗？
```

### 方式2: 回复机器人
1. 找到机器人发送的任何消息（如价格更新消息）
2. 点击"回复"
3. 输入你的问题

### 示例问题
- "什么是区块链？"
- "如何理财？"
- "黄金价格会涨吗？"
- "Python是什么？"

## 📊 功能特性

✅ 定时推送金融市场价格（每天7次）
✅ AI智能问答（支持@机器人或回复消息）
✅ 使用Google Gemini 2.0 Flash模型
✅ 自动显示"正在思考"状态
✅ 中文回答，简洁清晰

## 🔧 配置信息

- **AI服务**: Google Gemini
- **模型**: gemini-2.0-flash-exp
- **API密钥**: 已配置 ✅
- **状态**: 已启用 ✅

## 📝 测试AI功能

运行测试脚本：
```bash
python test_ai.py
```

## ⚙️ 调整设置

编辑 `config.py` 文件可以修改：
- `GEMINI_MODEL`: 更换AI模型
- `AI_MAX_TOKENS`: 调整回答长度
- `AI_TEMPERATURE`: 调整创造性（0-1）
- `AI_ENABLED`: 启用/禁用AI功能

## 📚 详细文档

- [AI功能详细配置](AI_SETUP.md)
- [完整README](README.md)

## ⚠️ 注意事项

1. 确保机器人在群组中有发送消息权限
2. 只有@机器人或回复机器人的消息才会触发AI回答
3. Google Gemini API有免费额度和速率限制
4. 不要将API密钥提交到公开代码库

## 🎉 开始使用

现在就启动机器人，在群组中@它提问吧！
