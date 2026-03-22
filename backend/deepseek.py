#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API 操作模块
封装 DeepSeek API 的调用
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")


def chat(messages):
    """
    调用 DeepSeek API
    
    参数:
        messages: 对话历史消息列表
    返回:
        AI 的回复内容字符串
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.3
    }
    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: {e}"


def check_api_key():
    """检查 API 密钥是否已配置"""
    return bool(API_KEY and API_KEY != "your_api_key_here")
