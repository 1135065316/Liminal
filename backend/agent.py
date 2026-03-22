#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Agent - 极简自动化执行
基于 'bash is all you need' 理念，输入任务，自动调用 bash/skill 完成
"""

import sys
from base_ops import WORK_DIR, run_command, get_skill_commands_help
from deepseek import chat, check_api_key
from conversation_logger import (
    generate_conversation_id,
    save_conversation,
    get_conversation_summary
)


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

    # 生成对话ID（基于开始时间的时间戳）
    conversation_id = generate_conversation_id()
    print(f"开始执行: {task}")
    print(f"对话ID: {conversation_id}\n")

    # 获取 skill 命令帮助
    skill_help = get_skill_commands_help()

    # 设置系统提示词
    system_msg = f"""你是自动化 Agent，工作目录: {WORK_DIR}
你的任务是分析需求，生成命令来逐步完成任务。

你可以使用两种类型的命令：
1. **Bash 命令**: 普通的 shell 命令，如 `ls -la`, `cat file.txt`
2. **Skill 命令**: 预定义的文件/代码操作函数，格式为 `函数名(参数1, 参数2, ...)`

规则:
- 每次只输出一个命令（bash 或 skill），不要解释
- 优先使用 skill 命令处理文件操作，更精确可靠
- 如果文件内容很长（超过 5000 字符），请分多次使用 append_to_file 追加写入，而不是一次性写入
- 如果任务完成，输出 DONE: 结果描述
- 如果无法完成，输出 FAIL: 原因

{skill_help}"""

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"任务: {task}\n\n请给出第一个命令:"}
    ]

    try:
        max_rounds = 20
        for i in range(max_rounds):
            response = chat(messages)
            
            if response.startswith("DONE:"):
                print(f"完成: {response}")
                messages.append({"role": "assistant", "content": response})
                break
            if response.startswith("FAIL:"):
                print(f"失败: {response}")
                messages.append({"role": "assistant", "content": response})
                break
            
            # 使用 run_command 自动识别并执行命令
            output = run_command(response.strip())
            print(f"  -> {output[:200]}{'...' if len(output) > 200 else ''}\n")
            
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": f"执行结果:\n{output}\n\n请继续（DONE: 完成 / FAIL: 失败 / 下一个命令）:"})
        else:
            print("达到最大轮数限制")
    finally:
        # 保存对话记录
        file_path = save_conversation(conversation_id, messages)
        print(f"\n对话已保存: {file_path}")
        print(get_conversation_summary(messages))


if __name__ == "__main__":
    main()
