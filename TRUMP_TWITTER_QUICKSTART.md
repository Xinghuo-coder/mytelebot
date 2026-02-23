# 川普推特监控 - 快速启动指南

## 1️⃣ 功能已添加

✅ 配置文件已更新 ([config.py](config.py))
✅ 监控功能已实现 ([bot.py](bot.py))
✅ 文档已创建 ([TRUMP_TWITTER_SETUP.md](TRUMP_TWITTER_SETUP.md))
✅ 测试脚本已创建 ([test_trump_twitter.py](test_trump_twitter.py))

## 2️⃣ 配置说明

在 [config.py](config.py) 中的新配置：

```python
# 川普推特监控配置
TRUMP_TWITTER_ENABLED = True  # 是否启用
TRUMP_TWITTER_USERNAME = "realDonaldTrump"  # 用户名
TRUMP_CHECK_INTERVAL = 3  # 检查间隔（分钟）
```

## 3️⃣ 测试步骤

### 测试推特获取功能

运行测试脚本查看是否能成功获取推文：

```bash
python test_trump_twitter.py
```

这个脚本会：
- 测试所有配置的 Nitter 实例
- 尝试获取最新推文
- 显示详细的调试信息

### 启动机器人

```bash
python bot.py
```

启动后，机器人会：
1. 立即检查一次川普推特
2. 每3分钟自动检查一次
3. 发现新推文时自动推送到群组

## 4️⃣ 验证功能

### 查看日志

启动后查看日志输出：
```
川普推特监控已启用，每3分钟检查一次
立即检查川普推特...
开始检查川普推特...
从 https://nitter.net 获取到 X 条推文
✅ 成功发送川普推文 ID: XXXXX
```

### 查看群组消息

成功后，你会在 Telegram 群组中看到如下格式的消息：

```
🐦 川普推特更新

[推文内容]

🔗 查看原推文
🕐 [发布时间]
```

## 5️⃣ 常见问题

### Q: 无法获取推文？

**A:** 运行测试脚本检查：
```bash
python test_trump_twitter.py
```

如果所有 Nitter 实例都失败，可以：
1. 添加更多 Nitter 镜像站到配置
2. 检查网络连接
3. 查看详细文档 [TRUMP_TWITTER_SETUP.md](TRUMP_TWITTER_SETUP.md)

### Q: 如何临时禁用此功能？

**A:** 在 [config.py](config.py) 中设置：
```python
TRUMP_TWITTER_ENABLED = False
```

### Q: 如何调整检查频率？

**A:** 修改 [config.py](config.py) 中的：
```python
TRUMP_CHECK_INTERVAL = 5  # 改为5分钟
```

建议：2-5分钟之间

### Q: 如何监控其他 Twitter 账号？

**A:** 修改 [config.py](config.py) 中的：
```python
TRUMP_TWITTER_USERNAME = "elonmusk"  # 例如马斯克
```

## 6️⃣ 文件说明

| 文件 | 说明 |
|------|------|
| [config.py](config.py) | 配置文件（已添加川普推特配置） |
| [bot.py](bot.py) | 主程序（已添加监控功能） |
| [TRUMP_TWITTER_SETUP.md](TRUMP_TWITTER_SETUP.md) | 详细功能文档 |
| [test_trump_twitter.py](test_trump_twitter.py) | 测试脚本 |
| sent_tweets.json | 已发送推文ID记录（自动生成） |

## 7️⃣ 工作原理

```
┌─────────────────┐
│   定时任务      │
│ (每3分钟运行)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 检查川普推特    │
│ (多数据源)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 过滤新推文      │
│ (检查ID是否     │
│  已发送)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 发送到Telegram  │
│ 群组            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 保存推文ID      │
│ (避免重复)      │
└─────────────────┘
```

## 8️⃣ 数据源说明

机器人使用多个数据源确保可靠性：

1. **Nitter** (主要)
   - 无需 API 密钥
   - 多个镜像站备份
   - 可能不稳定

2. **Twitter Syndication API** (备用)
   - Twitter 官方公开 API
   - 无需认证
   - 功能有限

## 9️⃣ 下一步

现在你可以：

1. ✅ 运行测试脚本验证功能
2. ✅ 启动机器人开始监控
3. ✅ 根据需要调整配置
4. ✅ 查看详细文档了解更多

## 🔟 获取帮助

- 详细文档: [TRUMP_TWITTER_SETUP.md](TRUMP_TWITTER_SETUP.md)
- 测试工具: `python test_trump_twitter.py`
- 查看日志: 启动 bot.py 后查看控制台输出

---

**提示**: 首次运行时，可能会推送最近的几条推文。之后只会推送新发布的推文。
