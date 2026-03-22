#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Agent - 极简自动化执行
基于 'bash is all you need' 理念，输入任务，自动调用 bash 完成
"""

import sys
from base_ops import WORK_DIR, run_bash
from deepseek import chat, check_api_key


def main():
    # 检查API密钥是否已配置
    if not check_api_key():
        print("请先配置 DEEPSEEK_API_KEY")
        return

    # 获取用户输入的任务
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = input("任务: ").strip()
    
    if not task:
        return

    print(f"开始执行: {task}\n")

    # 设置系统提示词
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
