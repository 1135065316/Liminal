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
from context_manager import (
    check_context_limit,
    Interruptible
)


def main():
    # 检查API密钥是否已配置
    if not check_api_key():
        print("请先配置 DEEPSEEK_API_KEY")
        return

    # 生成对话ID（基于开始时间的时间戳）
    conversation_id = generate_conversation_id()
    print(f"对话ID: {conversation_id}\n")

    # 获取 skill 命令帮助
    skill_help = get_skill_commands_help()

    # 设置系统提示词
    system_msg = f"""你是自动化 Agent，工作目录: {WORK_DIR}
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

    messages = [{"role": "system", "content": system_msg}]

    # 获取初始输入（命令行或交互式）
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        messages.append({"role": "user", "content": user_input})
    else:
        user_input = None  # 将在循环中获取

    try:
        round_num = 0
        while True:
            round_num += 1
            
            # 获取用户输入（首次交互式或任务完成后）
            if user_input is None:
                user_input = input("> ").strip()
                if not user_input:
                    break
                messages.append({"role": "user", "content": user_input})
                user_input = ""  # 标记为已处理，进入 AI 自动执行模式
            
            # 检查上下文长度
            is_limited, current_tokens, token_limit = check_context_limit(messages)
            if is_limited:
                break
            
            # 可中断的 API 调用
            with Interruptible(messages, "API请求") as op:
                response = chat(messages)
            if op.interrupted:
                break
            
            if response.startswith("DONE:"):
                print(f"完成: {response}")
                messages.append({"role": "assistant", "content": response})
                user_input = None  # 继续对话，下一轮获取输入
                continue
            
            if response.startswith("FAIL:"):
                print(f"失败: {response}")
                messages.append({"role": "assistant", "content": response})
                user_input = None  # 继续对话，下一轮获取输入
                continue
            
            # 可中断的命令执行
            with Interruptible(messages, "命令执行") as op:
                output = run_command(response.strip())
            if op.interrupted:
                break
            
            print(f"  -> {output[:200]}{'...' if len(output) > 200 else ''}\n")
            
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": f"执行结果:\n{output}\n\n请继续:"})
            
            # 显示当前 token 使用情况
            print(f"[上下文: {current_tokens}/{token_limit} tokens]")
            # user_input 保持原值，下一轮继续 AI 自动执行
    except KeyboardInterrupt:
        print("\n\n用户强制退出，正在保存对话...")
        messages.append({"role": "user", "content": "[用户强制退出]"})
    finally:
        # 保存对话记录
        file_path = save_conversation(conversation_id, messages)
        print(f"\n对话已保存: {file_path}")
        print(get_conversation_summary(messages))


if __name__ == "__main__":
    main()
