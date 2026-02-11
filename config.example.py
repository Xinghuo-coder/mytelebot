#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件模板 - 请复制此文件为 config.py 并填入您的真实配置
"""

# 电报机器人配置
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # 从 @BotFather 获取
CHAT_ID = "YOUR_CHAT_ID_HERE"  # 群组ID需要加负号前缀

# 定时任务配置
# 可以选择以下方式之一：

# 方式1: 每小时执行
# SCHEDULE_TYPE = "hourly"

# 方式2: 每天特定时间执行（小时列表）
SCHEDULE_TYPE = "daily"
SCHEDULE_HOURS = [7, 12, 15, 17, 21]  # 每天7:30, 12:00, 15:00, 17:50, 21:00
SCHEDULE_MINUTES = {7: 30, 17: 50}  # 7点推送时间为7:30，17点推送时间为17:50，其他为整点

# 方式3: 每隔N分钟执行
# SCHEDULE_TYPE = "interval"
# SCHEDULE_MINUTES = 30  # 每30分钟

# API配置
REQUEST_TIMEOUT = 10  # API请求超时时间（秒）

# AI配置（Google Gemini）
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Google Gemini API密钥，从 https://aistudio.google.com/app/apikey 获取
GEMINI_MODEL = "gemini-2.5-flash"  # 使用的AI模型 (推荐: gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash)
AI_MAX_TOKENS = 500  # AI回复的最大token数
AI_TEMPERATURE = 0.7  # 回复的创造性程度（0-1）
AI_ENABLED = True  # 是否启用AI功能
