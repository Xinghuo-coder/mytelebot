# 川普推特监控功能说明

## 功能概述

机器人现在可以实时监控川普（Donald Trump）的推特账号，并自动将新推文推送到Telegram群组。

## 配置说明

在 `config.py` 中已添加以下配置：

```python
# 川普推特监控配置
TRUMP_TWITTER_ENABLED = True  # 是否启用川普推特监控
TRUMP_TWITTER_USERNAME = "realDonaldTrump"  # 川普的Twitter用户名
TRUMP_CHECK_INTERVAL = 3  # 检查推特的时间间隔（分钟）
TRUMP_NITTER_INSTANCES = [  # Nitter实例列表（备用）
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
]
```

### 配置参数说明

- **TRUMP_TWITTER_ENABLED**: 设置为 `True` 启用功能，`False` 禁用功能
- **TRUMP_TWITTER_USERNAME**: Twitter用户名，默认为川普的官方账号
- **TRUMP_CHECK_INTERVAL**: 检查新推文的时间间隔（分钟），建议设置为 3-5 分钟
- **TRUMP_NITTER_INSTANCES**: Nitter镜像站列表，用于无需API密钥获取推文

## 工作原理

1. **多数据源策略**: 机器人使用多个数据源来获取推文：
   - Nitter (Twitter的开源前端，无需API密钥)
   - Twitter Syndication API (公开API)
   
2. **去重机制**: 使用 `sent_tweets.json` 文件记录已发送的推文ID，避免重复推送

3. **定时检查**: 每隔设定的时间间隔（默认3分钟）自动检查是否有新推文

4. **智能过滤**: 自动过滤转发和回复，只推送原创推文

## 消息格式

当检测到新推文时，机器人会发送如下格式的消息：

```
🐦 川普推特更新

[推文内容]

🔗 查看原推文
🕐 [发布时间]
```

## 注意事项

### 1. 关于数据源可用性

由于Twitter的API限制，本功能使用了以下备选方案：

- **Nitter**: 开源Twitter前端，但某些实例可能不稳定
- 如果Nitter实例失效，可以在配置中添加更多可用的Nitter镜像站

### 2. 监控频率建议

- **推荐间隔**: 3-5分钟
- **不建议**: 少于1分钟（可能被限流）
- **性能考虑**: 间隔越短，对网络和系统资源的消耗越大

### 3. 账号变更

如果需要监控其他Twitter账号，修改配置中的用户名即可：

```python
TRUMP_TWITTER_USERNAME = "其他用户名"
```

### 4. 数据存储

- `sent_tweets.json` 文件用于存储已发送的推文ID
- 自动保留最近100条推文记录
- 删除此文件将导致重新推送最近的推文

## 故障排查

### 问题1: 无法获取推文

**可能原因**:
- Nitter实例失效
- 网络连接问题
- Twitter账号被封禁或改名

**解决方案**:
1. 检查日志中的错误信息
2. 尝试访问配置中的Nitter实例，确认是否可用
3. 在配置中添加更多可用的Nitter镜像站

### 问题2: 重复推送推文

**可能原因**:
- `sent_tweets.json` 文件损坏或被删除

**解决方案**:
1. 确保 `sent_tweets.json` 文件权限正常
2. 检查日志中是否有文件读写错误

### 问题3: 推文延迟

**可能原因**:
- 检查间隔设置过长
- 数据源响应缓慢

**解决方案**:
1. 减小 `TRUMP_CHECK_INTERVAL` 的值（但不要低于2分钟）
2. 更换更快的Nitter实例

## 如何禁用此功能

如果不需要川普推特监控功能，在 `config.py` 中设置：

```python
TRUMP_TWITTER_ENABLED = False
```

## 添加更多Nitter镜像站

如果默认的Nitter实例不可用，可以在配置中添加更多镜像：

```python
TRUMP_NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.hu",
    "https://nitter.cz",
    # 添加更多可用的镜像站...
]
```

可以在 https://github.com/zedeus/nitter/wiki/Instances 查找更多可用的Nitter实例。

## 升级Twitter API（可选）

如果需要更稳定的服务，可以申请Twitter API密钥：

1. 访问 https://developer.twitter.com/
2. 创建开发者账号并申请API访问权限
3. 在代码中添加API密钥配置
4. 使用官方Twitter API替代Nitter

## 技术实现细节

- **异步请求**: 使用 `aiohttp` 进行非阻塞网络请求
- **HTML解析**: 使用正则表达式解析Nitter页面
- **定时任务**: 使用 `APScheduler` 管理定时任务
- **数据持久化**: 使用JSON文件存储已发送推文ID

## 更新日志

- **v1.0** (2026-02-23): 初始版本，支持基本的推特监控功能
