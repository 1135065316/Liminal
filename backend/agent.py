#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Agent - 极简自动化执行
输入任务，自动调用 bash 完成
"""

import os          # 导入操作系统模块，用于读取环境变量等
import sys         # 导入系统模块，用于获取命令行参数
import subprocess  # 导入子进程模块，用于执行系统命令
import requests    # 导入HTTP请求库，用于调用API
from dotenv import load_dotenv  # 导入加载.env文件的函数

load_dotenv()      # 加载.env文件中的环境变量

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")  # 从环境变量读取API密钥，默认为空字符串
API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")  # API地址
WORK_DIR = os.getcwd()  # 获取当前工作目录（程序运行所在的文件夹）

def chat(messages):
    """调用 DeepSeek API"""
    # 设置请求头，包含认证信息和内容类型
    headers = {
        "Authorization": f"Bearer {API_KEY}",  # 使用Bearer Token格式传递API密钥
        "Content-Type": "application/json"      # 告诉服务器发送的是JSON格式数据
    }
    # 设置请求体（要发送给AI的数据）
    payload = {
        "model": "deepseek-chat",   # 使用的AI模型名称
        "messages": messages,       # 对话历史记录
        "temperature": 0.3          #  creativity参数，越低越保守，越高越随机
    }
    try:
        # 发送POST请求到API，超时时间为120秒
        r = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()  # 如果返回错误状态码（如401, 500），抛出异常
        # 从JSON响应中提取AI的回复内容
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        # 如果出错了，返回错误信息字符串
        return f"ERROR: {e}"

def run_bash(cmd):
    """执行 bash 命令"""
    print(f"  $ {cmd}")  # 打印要执行的命令，前面加$表示命令行提示符
    try:
        # 运行shell命令，capture_output=True表示捕获输出，text=True表示以文本形式返回
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=300, cwd=WORK_DIR  # 超时5分钟，在指定工作目录执行
        )
        # 合并标准输出和标准错误输出
        output = result.stdout + result.stderr
        if not output:
            output = "(无输出)"  # 如果命令没有输出任何内容，显示"无输出"
        return output[:4000]  # 只返回前4000个字符，防止输出太长
    except subprocess.TimeoutExpired:
        return "ERROR: 命令超时"  # 命令执行超过5分钟
    except Exception as e:
        return f"ERROR: {e}"      # 其他错误

def main():
    # 检查API密钥是否已配置
    if not API_KEY or API_KEY == "your_api_key_here":
        print("请先配置 DEEPSEEK_API_KEY")
        return

    # 获取用户输入的任务
    if len(sys.argv) > 1:
        # 如果有命令行参数，把参数拼接成任务描述
        task = " ".join(sys.argv[1:])
    else:
        # 如果没有参数，提示用户输入任务
        task = input("任务: ").strip()
    
    # 如果任务为空，直接退出
    if not task:
        return

    print(f"开始执行: {task}\n")

    # 设置系统提示词，告诉AI它的角色和任务规则
    system_msg = f"""你是自动化 Agent，工作目录: {WORK_DIR}
你的任务是分析需求，生成 bash 命令来逐步完成任务。
每次只输出一个 bash 命令（单行或多行），不要解释。
如果任务完成，输出 DONE: 结果描述
如果无法完成，输出 FAIL: 原因"""

    # 初始化对话历史，包含系统提示和用户的第一条消息
    messages = [
        {"role": "system", "content": system_msg},  # system角色设定AI身份
        {"role": "user", "content": f"任务: {task}\n\n请给出第一个 bash 命令:"}  # user角色是用户输入
    ]

    max_rounds = 20  # 最多对话20轮，防止无限循环
    for i in range(max_rounds):
        # 调用AI获取回复
        response = chat(messages)
        
        # 检查AI是否标记任务完成
        if response.startswith("DONE:"):
            print(f"完成: {response}")
            return
        # 检查AI是否标记任务失败
        if response.startswith("FAIL:"):
            print(f"失败: {response}")
            return
        
        # 执行AI生成的bash命令
        output = run_bash(response.strip())
        # 打印命令执行结果，只显示前200个字符
        print(f"  -> {output[:200]}{'...' if len(output) > 200 else ''}\n")
        
        # 把AI的回复和命令执行结果添加到对话历史
        messages.append({"role": "assistant", "content": response})  # assistant角色是AI
        messages.append({"role": "user", "content": f"执行结果:\n{output}\n\n请继续（DONE: 完成 / FAIL: 失败 / 下一个命令）:"})

    # 如果超过20轮还没结束，打印提示
    print("达到最大轮数限制")

# 如果这个文件是直接运行的（不是被导入的），执行main函数
if __name__ == "__main__":
    main()
