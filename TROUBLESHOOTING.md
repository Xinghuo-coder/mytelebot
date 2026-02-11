# 机器人不回复消息 - 故障排查指南

## 问题：群组中@机器人后不回复

### ✅ 检查清单

- [ ] **1. 机器人隐私模式设置**
  - 找 @BotFather → `/setprivacy` → 选择机器人 → **Disable**
  - 这是最常见的问题！

- [ ] **2. 机器人在群组中的权限**
  - 方案A：关闭隐私模式（推荐）
  - 方案B：设置为群组管理员

- [ ] **3. 确认机器人正在运行**
  ```bash
  launchctl list | grep telebot
  # 应该看到 com.telebot
  ```

- [ ] **4. 检查群组ID是否正确**
  ```bash
  # 查看日志中的群组ID
  grep "群组ID" /Users/macbookpro/telebot/bot_error.log
  
  # 对比 config.py 中的 CHAT_ID
  grep CHAT_ID /Users/macbookpro/telebot/config.py
  ```

- [ ] **5. 查看实时日志**
  ```bash
  tail -f /Users/macbookpro/telebot/bot_error.log
  ```

### 🔧 常见问题解决

#### 问题1：隐私模式开启（最常见）
**症状**：日志只显示 getUpdates，没有"收到消息"
**解决**：@BotFather → `/setprivacy` → Disable

#### 问题2：群组ID不匹配
**症状**：日志显示"群组ID不匹配"
**解决**：
1. 从日志中复制正确的群组ID
2. 更新 `config.py` 中的 `CHAT_ID`
3. 重启机器人

#### 问题3：机器人用户名错误
**症状**：@机器人没反应
**解决**：
1. 在Telegram中检查机器人的实际用户名（@xxx）
2. 确保@的是正确的用户名

#### 问题4：AI API配置问题
**症状**：收到消息但AI不回复
**解决**：检查 Gemini API 密钥是否有效

### 📊 如何读取日志

正常工作时应该看到：
```
收到消息更新: Update(...)
消息文本: 你好, 群组ID: -5239428550, 配置的群组ID: -5239428550
机器人用户名: your_bot
是否@机器人: True, 是否回复机器人: False
收到问题: 你好
已回复问题: 你好...
```

### 🚀 重启机器人

```bash
# 停止
launchctl stop com.telebot

# 启动
launchctl start com.telebot

# 查看状态
launchctl list | grep telebot
```

### 📞 还是不行？

1. 确认完成了隐私模式设置
2. 重启机器人
3. 在群组中发送：`/start`（测试命令是否工作）
4. 然后发送：`@机器人用户名 测试`
5. 查看日志输出并提供给开发者
