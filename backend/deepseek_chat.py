#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek 简单问答脚本
命令行交互式对话
"""

import os
import sys
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")


def chat_with_deepseek(messages):
    """调用 DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"请求出错: {e}"


def main():
    # 检查 API Key
    if not API_KEY or API_KEY == "your_api_key_here":
        print("❌ 请先配置 DEEPSEEK_API_KEY")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 文件中填入你的 API Key")
        print("获取地址: https://platform.deepseek.com/")
        return

    print("🤖 DeepSeek 问答助手")
    print("输入你的问题，按 Enter 发送")
    print("输入 'quit' 或 'exit' 退出\n")

    # 对话历史
    messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手。请用中文回答问题。"}
    ]

    while True:
        try:
            user_input = input("👤 你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ("quit", "exit", "q"):
                print("👋 再见!")
                break

            # 添加用户消息
            messages.append({"role": "user", "content": user_input})
            
            # 调用 API
            print("🤖 AI: ", end="", flush=True)
            reply = chat_with_deepseek(messages)
            print(reply)
            print()
            
            # 添加 AI 回复到历史
            messages.append({"role": "assistant", "content": reply})
            
            # 限制历史长度（保留最近 10 轮）
            if len(messages) > 21:
                messages = [messages[0]] + messages[-20:]
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
