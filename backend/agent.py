#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Agent - 极简自动化执行
输入任务，自动调用 bash 完成
"""

import os
import sys
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
WORK_DIR = os.getcwd()

def chat(messages):
    """调用 DeepSeek API"""
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

def run_bash(cmd):
    """执行 bash 命令"""
    print(f"  $ {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=300, cwd=WORK_DIR
        )
        output = result.stdout + result.stderr
        if not output:
            output = "(无输出)"
        return output[:4000]
    except subprocess.TimeoutExpired:
        return "ERROR: 命令超时"
    except Exception as e:
        return f"ERROR: {e}"

def main():
    if not API_KEY or API_KEY == "your_api_key_here":
        print("请先配置 DEEPSEEK_API_KEY")
        return

    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("任务: ").strip()
    
    if not task:
        return

    print(f"开始执行: {task}\n")

    system_msg = f"""你是自动化 Agent，工作目录: {WORK_DIR}
你的任务是分析需求，生成 bash 命令来逐步完成任务。
每次只输出一个 bash 命令（单行或多行），不要解释。
如果任务完成，输出 DONE: 结果描述
如果无法完成，输出 FAIL: 原因"""

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"任务: {task}\n\n请给出第一个 bash 命令:"}
    ]

    max_rounds = 20
    for i in range(max_rounds):
        response = chat(messages)
        
        if response.startswith("DONE:"):
            print(f"完成: {response}")
            return
        if response.startswith("FAIL:"):
            print(f"失败: {response}")
            return
        
        output = run_bash(response.strip())
        print(f"  -> {output[:200]}{'...' if len(output) > 200 else ''}\n")
        
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"执行结果:\n{output}\n\n请继续（DONE: 完成 / FAIL: 失败 / 下一个命令）:"})

    print("达到最大轮数限制")

if __name__ == "__main__":
    main()
